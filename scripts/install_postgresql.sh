#!/bin/bash
###############################################################################
# PostgreSQL + pgvector 一键安装配置脚本
#
# 此脚本将自动完成：
# 1. 检查/安装 PostgreSQL
# 2. 启动并启用 PostgreSQL 服务
# 3. 安装 pgvector 扩展（从源码编译）
# 4. 创建数据库和用户
# 5. 授予权限
# 6. 启用 pgvector 扩展
# 7. 更新 .env 配置文件
#
# 使用方法：
#     sudo bash install_postgresql.sh
#
# 环境变量（可选）：
#     DB_NAME=wecom_db
#     DB_USER=wecom
#     DB_PASSWORD=wecom123
#     POSTGRES_PASSWORD=postgres123
###############################################################################

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置参数（适配企业微信智能客服系统）
DB_NAME="${DB_NAME:-wecom_db}"
DB_USER="${DB_USER:-wecom}"
DB_PASSWORD="${DB_PASSWORD:-wecom123}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres123}"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"

# 打印函数
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo ""
    echo "=============================================================================="
    echo "$1"
    echo "=============================================================================="
    echo ""
}

# 检查是否为 root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "此脚本需要 root 权限"
        echo "请使用: sudo bash $0"
        exit 1
    fi
}

# 以 postgres 用户执行命令（兼容无 sudo 环境）
run_as_postgres() {
    if command -v sudo >/dev/null 2>&1; then
        sudo -u postgres "$@"
    elif command -v runuser >/dev/null 2>&1; then
        runuser -u postgres -- "$@"
    else
        su - postgres -s /bin/bash -c "$*"
    fi
}

# PostgreSQL 服务控制（兼容无 systemd 环境）
control_postgresql() {
    local action=$1
    local data_dir="/var/lib/postgresql/${PG_MAJOR_VERSION}/main"

    if [ -z "$action" ]; then
        return 0
    fi

    if command -v pg_ctlcluster >/dev/null 2>&1; then
        pg_ctlcluster "${PG_MAJOR_VERSION}" main "${action}" >/dev/null 2>&1 || true
    elif command -v service >/dev/null 2>&1; then
        service postgresql "${action}" >/dev/null 2>&1 || true
    elif command -v pg_ctl >/dev/null 2>&1 && [ -d "$data_dir" ]; then
        run_as_postgres pg_ctl -D "$data_dir" "${action}" >/dev/null 2>&1 || true
    fi
}

# 步骤 1: 检查并安装 PostgreSQL
install_postgresql() {
    print_header "步骤 1/6: 安装 PostgreSQL"
    
    if command -v psql >/dev/null 2>&1; then
        PG_VERSION=$(psql --version | grep -oP '\d+\.\d+' | head -1)
        print_success "PostgreSQL 已安装 (版本: $PG_VERSION)"
        
        # 获取主版本号
        PG_MAJOR_VERSION=$(echo $PG_VERSION | cut -d. -f1)
    else
        print_info "正在安装 PostgreSQL..."
        apt-get update -qq
        DEBIAN_FRONTEND=noninteractive apt-get install -y postgresql postgresql-contrib
        
        PG_VERSION=$(psql --version | grep -oP '\d+\.\d+' | head -1)
        PG_MAJOR_VERSION=$(echo $PG_VERSION | cut -d. -f1)
        print_success "PostgreSQL 安装完成 (版本: $PG_VERSION)"
    fi
    
    # 启动服务（在容器中使用 pg_ctlcluster/service 兼容方式）
    print_info "启动 PostgreSQL 服务..."
    control_postgresql start
    
    # 等待服务启动
    sleep 3
    
    # 检查服务是否运行
    for i in {1..10}; do
        if pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
            print_success "PostgreSQL 服务正在运行"
            break
        fi
        if [ $i -eq 10 ]; then
            print_error "PostgreSQL 服务启动失败"
            print_info "尝试手动启动: sudo pg_ctlcluster ${PG_MAJOR_VERSION} main start"
            exit 1
        fi
        sleep 1
    done
    
    export PG_MAJOR_VERSION
}

# 步骤 2: 安装 pgvector 扩展
install_pgvector() {
    print_header "步骤 2/6: 安装 pgvector 扩展"
    
    # 检查 pgvector 是否已安装
    if run_as_postgres psql -d postgres -tAc "SELECT 1 FROM pg_available_extensions WHERE name='vector';" 2>/dev/null | grep -q 1; then
        print_success "pgvector 扩展已可用"
        return 0
    fi
    
    print_info "pgvector 扩展未安装，开始从源码编译安装..."
    
    # 安装编译依赖
    print_info "安装编译依赖..."
    apt-get update -qq
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        git build-essential \
        postgresql-server-dev-${PG_MAJOR_VERSION} \
        >/dev/null 2>&1
    
    # 创建工作目录
    WORK_DIR=$(mktemp -d)
    cd "$WORK_DIR"
    
    print_info "下载 pgvector 源码..."
    git clone --depth=1 --branch v0.5.1 https://github.com/pgvector/pgvector.git >/dev/null 2>&1
    cd pgvector
    
    print_info "编译 pgvector..."
    make >/dev/null 2>&1
    
    print_info "安装 pgvector..."
    make install >/dev/null 2>&1
    
    # 清理
    cd /
    rm -rf "$WORK_DIR"
    
    # 重启 PostgreSQL 以加载扩展
    print_info "重启 PostgreSQL 服务以加载扩展..."
    control_postgresql restart
    sleep 2
    
    print_success "pgvector 扩展安装完成"
}

# 步骤 3: 配置数据库和用户
setup_database() {
    print_header "步骤 3/6: 配置数据库和用户"
    
    # 备份并临时修改 pg_hba.conf
    HBA_FILE="/etc/postgresql/${PG_MAJOR_VERSION}/main/pg_hba.conf"
    BACKUP_FILE="${HBA_FILE}.bak.$(date +%Y%m%d_%H%M%S)"
    
    if [ ! -f "$BACKUP_FILE" ]; then
        print_info "备份 pg_hba.conf..."
        cp "$HBA_FILE" "$BACKUP_FILE"
    fi
    
    # 临时修改认证方式（仅用于设置）
    print_info "临时修改认证配置（允许本地信任连接）..."
    sed -i.tmp \
        -e 's/^local   all             postgres                                peer/local   all             postgres                                trust/' \
        -e 's/^host    all             all             127\.0\.0\.1\/32            scram-sha-256/host    all             all             127.0.0.1\/32            trust/' \
        "$HBA_FILE" 2>/dev/null || true
    
    # 重新加载配置
    control_postgresql reload
    sleep 1
    
    # 设置 postgres 用户密码
    print_info "设置 postgres 用户密码..."
    run_as_postgres psql -d postgres -c "ALTER USER postgres WITH PASSWORD '${POSTGRES_PASSWORD}';" >/dev/null 2>&1
    
    # 恢复原始配置
    print_info "恢复原始认证配置..."
    cp "$BACKUP_FILE" "$HBA_FILE"
    control_postgresql reload
    sleep 1
    
    # 使用密码连接执行后续操作
    export PGPASSWORD="$POSTGRES_PASSWORD"
    
    # 创建数据库
    print_info "创建数据库: $DB_NAME"
    if psql -h localhost -U postgres -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';" 2>/dev/null | grep -q 1; then
        print_warning "数据库 $DB_NAME 已存在"
    else
        psql -h localhost -U postgres -d postgres -c "CREATE DATABASE \"$DB_NAME\";" >/dev/null 2>&1
        print_success "数据库 $DB_NAME 创建成功"
    fi
    
    # 创建用户
    print_info "创建用户: $DB_USER"
    if psql -h localhost -U postgres -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER';" 2>/dev/null | grep -q 1; then
        print_warning "用户 $DB_USER 已存在，更新密码..."
        psql -h localhost -U postgres -d postgres -c "ALTER USER \"$DB_USER\" WITH PASSWORD '${DB_PASSWORD}';" >/dev/null 2>&1
    else
        psql -h localhost -U postgres -d postgres -c "CREATE USER \"$DB_USER\" WITH PASSWORD '${DB_PASSWORD}';" >/dev/null 2>&1
        print_success "用户 $DB_USER 创建成功"
    fi
    
    # 授予数据库权限
    print_info "授予数据库权限..."
    psql -h localhost -U postgres -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE \"$DB_NAME\" TO \"$DB_USER\";" >/dev/null 2>&1
    
    # 授予 schema 权限
    print_info "授予 schema 权限..."
    psql -h localhost -U postgres -d "$DB_NAME" -c "GRANT ALL ON SCHEMA public TO \"$DB_USER\";" >/dev/null 2>&1
    psql -h localhost -U postgres -d "$DB_NAME" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO \"$DB_USER\";" >/dev/null 2>&1
    psql -h localhost -U postgres -d "$DB_NAME" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO \"$DB_USER\";" >/dev/null 2>&1
    
    unset PGPASSWORD
    print_success "数据库配置完成"
}

# 步骤 4: 启用 pgvector 和 uuid-ossp 扩展
enable_pgvector() {
    print_header "步骤 4/6: 启用数据库扩展"
    
    export PGPASSWORD="$POSTGRES_PASSWORD"
    
    print_info "在数据库 $DB_NAME 中启用 pgvector 扩展..."
    if psql -h localhost -U postgres -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS vector;" >/dev/null 2>&1; then
        VERSION=$(psql -h localhost -U postgres -d "$DB_NAME" -tAc "SELECT extversion FROM pg_extension WHERE extname='vector';" 2>/dev/null)
        if [ -n "$VERSION" ]; then
            print_success "pgvector 扩展启用成功 (版本: $VERSION)"
        else
            print_warning "pgvector 扩展可能未正确启用"
        fi
    else
        print_error "pgvector 扩展启用失败"
        print_info "可能需要手动安装 pgvector 扩展"
        return 1
    fi
    
    print_info "在数据库 $DB_NAME 中启用 uuid-ossp 扩展..."
    if psql -h localhost -U postgres -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";" >/dev/null 2>&1; then
        print_success "uuid-ossp 扩展启用成功"
    else
        print_warning "uuid-ossp 扩展启用失败（可选扩展）"
    fi
    
    unset PGPASSWORD
}

# 步骤 5: 更新 .env 文件
update_env_file() {
    print_header "步骤 5/6: 更新 .env 配置文件"
    
    ENV_DIR="$(dirname "$ENV_FILE")"
    mkdir -p "$ENV_DIR"
    
    # 生成数据库 URL（异步和同步两种）
    DATABASE_URL="postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}"
    DATABASE_URL_SYNC="postgresql://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}"
    
    print_info "更新 $ENV_FILE"
    
    # 如果文件不存在，创建它
    if [ ! -f "$ENV_FILE" ]; then
        touch "$ENV_FILE"
    fi
    
    # 更新或添加 DATABASE_URL（异步）
    if grep -q "^DATABASE_URL=" "$ENV_FILE"; then
        sed -i "s|^DATABASE_URL=.*|DATABASE_URL=${DATABASE_URL}|" "$ENV_FILE"
        print_success "DATABASE_URL 已更新"
    else
        echo "" >> "$ENV_FILE"
        echo "# PostgreSQL 数据库配置" >> "$ENV_FILE"
        echo "DATABASE_URL=${DATABASE_URL}" >> "$ENV_FILE"
        print_success "DATABASE_URL 已添加"
    fi
    
    # 更新或添加 DATABASE_URL_SYNC（同步）
    if grep -q "^DATABASE_URL_SYNC=" "$ENV_FILE"; then
        sed -i "s|^DATABASE_URL_SYNC=.*|DATABASE_URL_SYNC=${DATABASE_URL_SYNC}|" "$ENV_FILE"
        print_success "DATABASE_URL_SYNC 已更新"
    else
        echo "DATABASE_URL_SYNC=${DATABASE_URL_SYNC}" >> "$ENV_FILE"
        print_success "DATABASE_URL_SYNC 已添加"
    fi
    
    print_info "配置文件内容:"
    echo "  DATABASE_URL=${DATABASE_URL}"
    echo "  DATABASE_URL_SYNC=${DATABASE_URL_SYNC}"
}

# 步骤 6: 验证安装
verify_installation() {
    print_header "步骤 6/6: 验证安装"
    
    print_info "测试数据库连接..."
    export PGPASSWORD="$DB_PASSWORD"
    
    if psql -h localhost -U "$DB_USER" -d "$DB_NAME" -c "SELECT version();" >/dev/null 2>&1; then
        print_success "数据库连接测试成功"
    else
        print_error "数据库连接测试失败"
        return 1
    fi
    
    print_info "检查 pgvector 扩展..."
    VERSION=$(psql -h localhost -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT extversion FROM pg_extension WHERE extname='vector';" 2>/dev/null)
    if [ -n "$VERSION" ]; then
        print_success "pgvector 扩展已启用 (版本: $VERSION)"
    else
        print_warning "pgvector 扩展未启用"
    fi
    
    unset PGPASSWORD
}

# 主函数
main() {
    print_header "PostgreSQL + pgvector 一键安装配置脚本"
    
    print_info "配置信息:"
    echo "  数据库名: $DB_NAME"
    echo "  用户名: $DB_USER"
    echo "  用户密码: $(printf '*%.0s' {1..${#DB_PASSWORD}})"
    echo "  postgres 密码: $(printf '*%.0s' {1..${#POSTGRES_PASSWORD}})"
    echo ""
    
    # 检查 root 权限
    check_root
    
    # 执行安装步骤
    install_postgresql
    install_pgvector
    setup_database
    enable_pgvector
    update_env_file
    verify_installation
    
    # 完成
    print_header "✅ 安装配置完成！"
    
    echo ""
    print_success "PostgreSQL 和 pgvector 已成功安装并配置"
    echo ""
    echo "📋 配置信息:"
    echo "  数据库名: $DB_NAME"
    echo "  用户名: $DB_USER"
    echo "  密码: $DB_PASSWORD"
    echo ""
    echo "📝 数据库连接字符串已添加到: $ENV_FILE"
    echo "   DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}"
    echo "   DATABASE_URL_SYNC=postgresql://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}"
    echo ""
    echo "🚀 下一步:"
    echo "   1. 检查配置文件: cat $ENV_FILE"
    echo "   2. 测试连接: PGPASSWORD=$DB_PASSWORD psql -h localhost -U $DB_USER -d $DB_NAME"
    echo "   3. 运行数据库迁移: cd $PROJECT_ROOT && source venv/bin/activate && alembic upgrade head"
    echo "   4. 启动应用: cd $PROJECT_ROOT && source venv/bin/activate && uvicorn app.main:app --reload"
    echo ""
}

# 运行主函数
main "$@"

