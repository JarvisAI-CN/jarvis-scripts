#!/bin/bash

# WordPress 自动发布脚本 - Notion AI
# 使用 curl 直接操作 WordPress

WP_URL="https://dh.dhmip.cn"
COOKIE_FILE="/tmp/wp_cookies.txt"

# Notion AI 内容
TITLE="Notion AI - AI智能写作与文档管理平台"
SITE_URL="https://www.notion.so/product/ai"
CATEGORY_ID="25"  # 写作助手分类

# 准备内容（HTML格式）
CONTENT=$(cat <<'EOF'
<h2>AI智能写作与文档管理平台</h2>

<p>Notion AI 是一款集成在 Notion 工作空间中的强大AI助手，它不仅仅是一个写作工具，更是一个完整的AI工作平台。与大多数只停留在创意阶段的AI工具不同，Notion AI 能够帮你完成从构思到成稿的全流程工作。</p>

<h3>核心功能</h3>

<p>Notion AI 提供了多样化的智能服务。它支持<strong>自动生成会议纪要</strong>，并能进行<strong>深入研究</strong>来创建详细的文档和报告。<strong>内容生成与编辑</strong>功能让创作更加流畅，还能<strong>自动填充数据库</strong>的摘要和洞察。<strong>多语言翻译</strong>、<strong>流程图和图表生成</strong>、<strong>智能搜索</strong>以及<strong>数据库设置</strong>功能，都能显著提升工作效率。</p>

<h3>特色亮点</h3>

<p>安全性方面，Notion AI 采用了业界领先的数据保护措施。平台<strong>承诺不会使用客户数据训练模型</strong>，所有数据传输都采用TLS 1.2+加密，并提供细粒度的权限控制。平台已通过<strong>GDPR、CCPA、SOC 2 Type 2和ISO 27001</strong>等多项国际安全认证，确保数据安全得到最高级别的保护。此外，LLM提供商不会存储任何数据，企业版还支持<strong>零数据保留政策</strong>。</p>

<h3>适用人群</h3>

<p>Notion AI 适合各类用户群体。<strong>知识工作者</strong>可以用于笔记管理和文档协作，<strong>创作者</strong>能够获得灵感激发和内容生成支持，<strong>产品经理</strong>可以用它来构建知识库，<strong>企业团队</strong>则能利用AI进行深度研究和报告生成。对于<strong>学生和研究人员</strong>，它同样是强大的学习和研究工具。</p>

<h3>总结推荐</h3>

<p>Notion AI 的核心优势在于<strong>深度整合到Notion工作空间</strong>，实现了"一个平台完成所有工作"的理念。它支持<strong>GPT-4.1、Claude 4</strong>等多种AI模型，并通过<strong>MCP协议</strong>连接第三方应用。<strong>AI会议笔记</strong>功能可以帮助团队轻松转录会议内容并提取关键信息。定价方面，Business和Enterprise计划已包含Notion AI功能，其他计划提供有限的试用额度。对于寻求一体化AI工作平台的用户来说，Notion AI是值得投资的选择。</p>

<p>THE END</p>

<h2>访问建议</h2>

<p>为确保最佳使用体验，建议通过浏览器访问 Notion AI 官网。微信或QQ可能会屏蔽相关链接，请使用浏览器直接访问。推荐使用未屏蔽网址的浏览器，如苹果设备自带的Safari浏览器、谷歌Chrome或微软Edge等主流浏览器。如果遇到访问问题，请检查网络连接或使用VPN切换到更稳定的运营商网络。</p>
EOF
)

echo "============================================================"
echo "🚀 WordPress 自动发布脚本 - Notion AI"
echo "============================================================"
echo ""

# 步骤 1: 登录 WordPress
echo "📝 步骤 1: 登录 WordPress..."
curl -s -c "$COOKIE_FILE" \
  -X POST "${WP_URL}/wp-login.php" \
  -d "log=admin" \
  -d "pwd=fs123456" \
  -d "wp-submit=登录" \
  -d "redirect_to=${WP_URL}/wp-admin/" \
  -d "testcookie=1" \
  -L > /dev/null

# 检查登录是否成功
if grep -q "wordpress_logged_in" "$COOKIE_FILE"; then
    echo "✅ 登录成功"
else
    echo "❌ 登录失败"
    exit 1
fi

# 步骤 2: 访问添加新网址页面，获取表单数据
echo ""
echo "📝 步骤 2: 获取表单数据..."
PAGE_HTML=$(curl -s -b "$COOKIE_FILE" "${WP_URL}/wp-admin/post-new.php?post_type=sites")

# 提取 post_ID
POST_ID=$(echo "$PAGE_HTML" | grep -oP 'name="post_ID"\s+value="\K[^"]+' | head -1)
if [ -z "$POST_ID" ]; then
    POST_ID=$(echo "$PAGE_HTML" | grep -oP 'id="post_ID"\s+value="\K[^"]+' | head -1)
fi
if [ -z "$POST_ID" ]; then
    # 尝试另一种格式
    POST_ID=$(echo "$PAGE_HTML" | grep -oE 'post_ID.*?value="([0-9]+)' | grep -oE '[0-9]+' | head -1)
fi
echo "📌 文章ID: $POST_ID"

# 提取 _wpnonce
WP_NONCE=$(echo "$PAGE_HTML" | grep -oP 'name="_wpnonce" value="\K[^"]+')
echo "🔑 Nonce: $WP_NONCE"

# 提取其他必要的 hidden 字段
USER_ID=$(echo "$PAGE_HTML" | grep -oP 'id="user-id" name="user_ID" value="\K[^"]+')
HIDDEN_ACTION=$(echo "$PAGE_HTML" | grep -oP 'id="hiddenaction" name="action" value="\K[^"]+')
POST_TYPE=$(echo "$PAGE_HTML" | grep -oP 'id="post_type" name="post_type" value="\K[^"]+')
ORIGINAL_POST_STATUS=$(echo "$PAGE_HTML" | grep -oP 'id="original_post_status" name="original_post_status" value="\K[^"]+')

echo "📋 表单字段提取完成"

# 步骤 3: 发布文章
echo ""
echo "📝 步骤 3: 发布文章..."
echo "📌 标题: $TITLE"
echo "🔗 链接: $SITE_URL"
echo "📁 分类ID: $CATEGORY_ID (写作助手)"

# 发布文章（使用 wp-admin/post.php 的接口）
RESPONSE=$(curl -s -b "$COOKIE_FILE" \
  -X POST "${WP_URL}/wp-admin/post.php" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "_wpnonce=$WP_NONCE" \
  -d "_wp_http_referer=/wp-admin/post-new.php?post_type=sites" \
  -d "user_ID=$USER_ID" \
  -d "action=editpost" \
  -d "originalaction=editpost" \
  -d "post_author=1" \
  -d "post_type=$POST_TYPE" \
  -d "post_ID=$POST_ID" \
  -d "original_post_status=$ORIGINAL_POST_STATUS" \
  -d "auto_draft=1" \
  -d "post_title=$TITLE" \
  -d "content=$CONTENT" \
  --data-urlencode "site_url=$SITE_URL" \
  -d "tax_input[favorites][]=$CATEGORY_ID" \
  -d "post_status=publish" \
  -d "publish=发布" \
  -L)

# 检查是否发布成功
if echo "$RESPONSE" | grep -q "文章已发布"; then
    echo "✅ 文章发布成功"
elif echo "$RESPONSE" | grep -q "wordpress已为您自动保存草稿"; then
    echo "✅ 文章已保存（可能是草稿）"
elif echo "$RESPONSE" | grep -q "post.php?post=$POST_ID"; then
    echo "✅ 文章发布成功"
else
    echo "⚠️  发布状态未知，请手动确认"
fi

# 步骤 4: 获取文章链接
echo ""
echo "📝 步骤 4: 获取文章链接..."

# 尝试从响应中提取文章链接
if echo "$RESPONSE" | grep -q 'sample-permalink'; then
    POST_LINK=$(echo "$RESPONSE" | grep -oP 'href="https://dh\.dmip\.cn/sites/\K[^"]+' | head -1)
    if [ -n "$POST_LINK" ]; then
        echo "✅ 文章链接: https://dh.dhmip.cn/sites/$POST_LINK"
    else
        echo "🔗 文章链接: https://dh.dhmip.cn/sites/?p=$POST_ID"
    fi
else
    echo "🔗 文章链接: https://dh.dhmip.cn/sites/?p=$POST_ID"
fi

# 清理
rm -f "$COOKIE_FILE"

echo ""
echo "============================================================"
echo "✅ 发布完成！"
echo "============================================================"
