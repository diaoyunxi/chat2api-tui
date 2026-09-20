#!/bin/bash
# ============================================================
# Chat2API + TUI Client 一键部署脚本
# 用法: curl -fsSL https://your-domain.com/install.sh | bash
# 或:   bash install.sh
# ============================================================

set -e

# ---------- 颜色定义 ----------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ---------- 配置 ----------
CHAT2API_REPO="https://github.com/xiaoY233/Chat2API.git"
CLIENT_REPO="https://github.com/yourusername/chat2api-tui-client.git"  # 替换为你的仓库地址
INSTALL_DIR="$HOME/chat2api-deploy"
CHAT2API_DIR="$INSTALL_DIR/Chat2API"
CLIENT_DIR="$INSTALL_DIR/chat2api-tui-client"
CHAT2API_PORT=8080

# ---------- 辅助函数 ----------
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "$1 未安装，请先安装后再运行"
        return 1
    fi
    return 0
}

# ---------- 检测操作系统 ----------
detect_os() {
    case "$(uname -s)" in
        Linux*)     OS="linux";;
        Darwin*)    OS="macos";;
        CYGWIN*|MINGW*|MSYS*) OS="windows";;
        *)          OS="unknown";;
    esac
    print_info "检测到操作系统: $OS"
}

# ---------- 安装 Node.js（如未安装） ----------
install_nodejs() {
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node -v)
        print_info "Node.js 已安装: $NODE_VERSION"
        return 0
    fi

    print_warning "Node.js 未安装，正在自动安装..."

    case "$OS" in
        linux)
            # 使用 NodeSource 官方脚本
            curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
            sudo apt-get install -y nodejs
            ;;
        macos)
            # 使用 Homebrew 安装
            if ! command -v brew &> /dev/null; then
                print_error "请先安装 Homebrew: https://brew.sh/"
                return 1
            fi
            brew install node
            ;;
        windows)
            print_error "Windows 请手动安装 Node.js: https://nodejs.org/"
            return 1
            ;;
        *)
            print_error "不支持的操作系统，请手动安装 Node.js 18+"
            return 1
            ;;
    esac

    if command -v node &> /dev/null; then
        print_success "Node.js 安装成功: $(node -v)"
    else
        print_error "Node.js 安装失败，请手动安装"
        return 1
    fi
}

# ---------- 安装 Python 和 pip（如未安装） ----------
install_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -v 2>&1 | head -n1)
        print_info "Python3 已安装: $PYTHON_VERSION"
        return 0
    fi

    print_warning "Python3 未安装，正在自动安装..."

    case "$OS" in
        linux)
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
            ;;
        macos)
            if ! command -v brew &> /dev/null; then
                print_error "请先安装 Homebrew: https://brew.sh/"
                return 1
            fi
            brew install python3
            ;;
        windows)
            print_error "Windows 请手动安装 Python: https://www.python.org/"
            return 1
            ;;
        *)
            print_error "不支持的操作系统，请手动安装 Python 3.8+"
            return 1
            ;;
    esac

    if command -v python3 &> /dev/null; then
        print_success "Python3 安装成功"
    else
        print_error "Python3 安装失败，请手动安装"
        return 1
    fi
}

# ---------- 安装 Git（如未安装） ----------
install_git() {
    if command -v git &> /dev/null; then
        print_info "Git 已安装"
        return 0
    fi

    print_warning "Git 未安装，正在自动安装..."

    case "$OS" in
        linux)
            sudo apt-get update
            sudo apt-get install -y git
            ;;
        macos)
            if ! command -v brew &> /dev/null; then
                print_error "请先安装 Homebrew: https://brew.sh/"
                return 1
            fi
            brew install git
            ;;
        windows)
            print_error "Windows 请手动安装 Git: https://git-scm.com/"
            return 1
            ;;
        *)
            print_error "不支持的操作系统，请手动安装 Git"
            return 1
            ;;
    esac

    if command -v git &> /dev/null; then
        print_success "Git 安装成功"
    else
        print_error "Git 安装失败，请手动安装"
        return 1
    fi
}

# ---------- 部署 Chat2API ----------
deploy_chat2api() {
    print_info "========== 部署 Chat2API =========="

    if [ -d "$CHAT2API_DIR" ]; then
        print_warning "Chat2API 目录已存在，跳过克隆"
        cd "$CHAT2API_DIR"
    else
        print_info "克隆 Chat2API 仓库..."
        git clone "$CHAT2API_REPO" "$CHAT2API_DIR"
        cd "$CHAT2API_DIR"
    fi

    print_info "安装 npm 依赖..."
    npm install

    print_info "构建 Chat2API..."
    npm run build

    print_success "Chat2API 构建完成"

    # 创建启动脚本
    cat > "$INSTALL_DIR/start-chat2api.sh" << 'EOF'
#!/bin/bash
cd "$1"
npx electron-vite dev 2>&1
EOF
    chmod +x "$INSTALL_DIR/start-chat2api.sh"

    print_info "Chat2API 启动命令: $INSTALL_DIR/start-chat2api.sh"
    print_info "或手动进入 $CHAT2API_DIR 执行: npx electron-vite dev"
}

# ---------- 部署客户端 ----------
deploy_client() {
    print_info "========== 部署 Chat2API TUI Client =========="

    if [ -d "$CLIENT_DIR" ]; then
        print_warning "客户端目录已存在，跳过克隆"
        cd "$CLIENT_DIR"
    else
        print_info "克隆客户端仓库..."
        git clone "$CLIENT_REPO" "$CLIENT_DIR"
        cd "$CLIENT_DIR"
    fi

    print_info "创建 Python 虚拟环境..."
    python3 -m venv venv
    source venv/bin/activate

    print_info "安装 Python 依赖..."
    pip install --upgrade pip
    pip install -r requirements.txt

    print_info "创建配置文件..."
    if [ ! -f "config.yml" ]; then
        cp config.example.yml config.yml
        print_warning "请编辑 $CLIENT_DIR/config.yml，填入你的 API Key"
    else
        print_info "config.yml 已存在"
    fi

    print_success "客户端部署完成"

    # 创建启动脚本
    cat > "$INSTALL_DIR/start-client.sh" << 'EOF'
#!/bin/bash
cd "$1"
source venv/bin/activate
python app.py
EOF
    chmod +x "$INSTALL_DIR/start-client.sh"

    print_info "客户端启动命令: $INSTALL_DIR/start-client.sh"
    print_info "或手动进入 $CLIENT_DIR 执行: source venv/bin/activate && python app.py"
}

# ---------- 显示后续步骤 ----------
show_next_steps() {
    echo ""
    echo "============================================================"
    echo -e "${GREEN}✅ 所有组件部署完成！${NC}"
    echo "============================================================"
    echo ""
    echo "📌 后续步骤："
    echo ""
    echo "1️⃣ 启动 Chat2API 服务端（新终端）："
    echo "   $INSTALL_DIR/start-chat2api.sh"
    echo ""
    echo "2️⃣ 配置 Chat2API："
    echo "   - 打开浏览器访问 http://127.0.0.1:$CHAT2API_PORT"
    echo "   - 添加 AI 服务商（DeepSeek/GLM/Kimi 等）"
    echo "   - 在设置中生成 API Key"
    echo ""
    echo "3️⃣ 编辑客户端配置文件："
    echo "   vi $CLIENT_DIR/config.yml"
    echo "   - 填入 Chat2API 地址: http://127.0.0.1:$CHAT2API_PORT/v1"
    echo "   - 填入上一步生成的 API Key"
    echo ""
    echo "4️⃣ 启动客户端（新终端）："
    echo "   $INSTALL_DIR/start-client.sh"
    echo ""
    echo "📂 安装目录: $INSTALL_DIR"
    echo "============================================================"
}

# ---------- 主流程 ----------
main() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║  🚀 Chat2API + TUI Client 一键部署脚本                  ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""

    # 检测操作系统
    detect_os

    # 创建安装目录
    mkdir -p "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    print_info "安装目录: $INSTALL_DIR"

    # 检查并安装依赖
    install_git || exit 1
    install_nodejs || exit 1
    install_python || exit 1

    # 部署 Chat2API
    deploy_chat2api || exit 1

    # 部署客户端
    deploy_client || exit 1

    # 显示后续步骤
    show_next_steps
}

# ---------- 执行 ----------
main "$@"
