#!/bin/bash
# Git提交前检查脚本
# 检查CI状态、代码质量等

set -euo pipefail

WORKSPACE="/home/ubuntu/.openclaw/workspace"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Git提交前检查"
echo "=========================================="

# 1. 检查是否有暂存的更改
if [ -z "$(git diff --cached --name-only)" ]; then
    echo -e "${YELLOW}⚠️  没有暂存的更改${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 有暂存的更改${NC}"

# 2. 检查是否在Git仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ 不在Git仓库中${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 在Git仓库中${NC}"

# 3. 检查gh命令
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}⚠️  gh命令未安装，跳过GitHub检查${NC}"
else
    # 4. 检查最新PR的CI状态（如果存在PR）
    CURRENT_REPO=$(git remote get-url origin | sed -E 's|.*github.com[/:]||' | sed 's|\.git$||')

    if gh pr list --repo "$CURRENT_REPO" --limit 1 --json number --jq '.[0].number' > /dev/null 2>&1; then
        LATEST_PR=$(gh pr list --repo "$CURRENT_REPO" --limit 1 --json number,state --jq '.[0]')
        PR_STATE=$(echo "$LATEST_PR" | jq -r '.state')

        if [ "$PR_STATE" = "OPEN" ]; then
            echo -e "${GREEN}✓ 检查最新PR的CI状态...${NC}"

            # 获取CI状态
            CI_OUTPUT=$(gh pr checks --repo "$CURRENT_REPO" 2>&1)

            if echo "$CI_OUTPUT" | grep -q "fail"; then
                echo -e "${RED}❌ CI检查失败！${NC}"
                echo "$CI_OUTPUT"
                echo -e "${YELLOW}建议：修复CI失败后再提交${NC}"
                exit 1
            else
                echo -e "${GREEN}✓ CI检查通过${NC}"
            fi
        fi
    fi
fi

# 5. 检查Python代码质量
if command -v ruff &> /dev/null; then
    echo -e "${GREEN}✓ 检查Python代码质量...${NC}"

    STAGED_PY_FILES=$(git diff --cached --name-only | grep '\.py$' || true)

    if [ -n "$STAGED_PY_FILES" ]; then
        RUFF_ISSUES=0
        for file in $STAGED_PY_FILES; do
            if [ -f "$file" ]; then
                ISSUES=$(ruff check "$file" 2>&1 | wc -l || echo 0)
                if [ "$ISSUES" -gt 0 ]; then
                    echo -e "${YELLOW}⚠️  $file: $ISSUES 个问题${NC}"
                    RUFF_ISSUES=$((RUFF_ISSUES + ISSUES))
                fi
            fi
        done

        if [ "$RUFF_ISSUES" -gt 0 ]; then
            echo -e "${YELLOW}⚠️  发现 $RUFF_ISSUES 个代码问题${NC}"
            echo -e "${YELLOW}建议：运行 'ruff check' 修复${NC}"
        else
            echo -e "${GREEN}✓ Python代码质量检查通过${NC}"
        fi
    fi
fi

# 6. 检查提交消息格式（如果提供了）
COMMIT_MSG_FILE="$1"

if [ -n "$COMMIT_MSG_FILE" ] && [ -f "$COMMIT_MSG_FILE" ]; then
    echo -e "${GREEN}✓ 检查提交消息格式...${NC}"

    COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

    # 检查是否有空提交
    if [ -z "$COMMIT_MSG" ]; then
        echo -e "${RED}❌ 提交消息为空${NC}"
        exit 1
    fi

    # 检查长度（建议不超过72字符）
    FIRST_LINE=$(echo "$COMMIT_MSG" | head -1)
    if [ ${#FIRST_LINE} -gt 72 ]; then
        echo -e "${YELLOW}⚠️  第一行超过72字符（${#FIRST_LINE}）${NC}"
    fi

    echo -e "${GREEN}✓ 提交消息格式检查通过${NC}"
fi

echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}✅ 所有检查通过，可以提交${NC}"
echo -e "${GREEN}==========================================${NC}"

exit 0
