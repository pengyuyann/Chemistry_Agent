# Chemistry Agent API 环境变量设置脚本 (PowerShell)
# 以管理员身份运行此脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Chemistry Agent API 环境变量设置" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否以管理员身份运行
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "⚠️  请以管理员身份运行此脚本！" -ForegroundColor Yellow
    Write-Host "右键点击PowerShell -> 以管理员身份运行" -ForegroundColor Yellow
    Read-Host "按任意键退出"
    exit
}

Write-Host "请按照提示输入你的API密钥：" -ForegroundColor Green
Write-Host ""

# 获取用户输入
$DEEPSEEK_API_KEY = Read-Host "请输入你的 DeepSeek API Key"
$OPENAI_API_KEY = Read-Host "请输入你的 OpenAI API Key (可选，直接回车跳过)"
$SERP_API_KEY = Read-Host "请输入你的 SERP API Key (可选，直接回车跳过)"
$RXN4CHEM_API_KEY = Read-Host "请输入你的 RXN4Chem API Key (可选，直接回车跳过)"
$CHEMSPACE_API_KEY = Read-Host "请输入你的 ChemSpace API Key (可选，直接回车跳过)"
$SEMANTIC_SCHOLAR_API_KEY = Read-Host "请输入你的 Semantic Scholar API Key (可选，直接回车跳过)"

Write-Host ""
Write-Host "正在设置环境变量..." -ForegroundColor Yellow

# 设置环境变量
try {
    # 设置必需的环境变量
    [Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", $DEEPSEEK_API_KEY, "User")
    Write-Host "✅ DEEPSEEK_API_KEY 已设置" -ForegroundColor Green
    
    # 设置可选的环境变量
    if ($OPENAI_API_KEY) {
        [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", $OPENAI_API_KEY, "User")
        Write-Host "✅ OPENAI_API_KEY 已设置" -ForegroundColor Green
    }
    
    if ($SERP_API_KEY) {
        [Environment]::SetEnvironmentVariable("SERP_API_KEY", $SERP_API_KEY, "User")
        Write-Host "✅ SERP_API_KEY 已设置" -ForegroundColor Green
    }
    
    if ($RXN4CHEM_API_KEY) {
        [Environment]::SetEnvironmentVariable("RXN4CHEM_API_KEY", $RXN4CHEM_API_KEY, "User")
        Write-Host "✅ RXN4CHEM_API_KEY 已设置" -ForegroundColor Green
    }
    
    if ($CHEMSPACE_API_KEY) {
        [Environment]::SetEnvironmentVariable("CHEMSPACE_API_KEY", $CHEMSPACE_API_KEY, "User")
        Write-Host "✅ CHEMSPACE_API_KEY 已设置" -ForegroundColor Green
    }
    
    if ($SEMANTIC_SCHOLAR_API_KEY) {
        [Environment]::SetEnvironmentVariable("SEMANTIC_SCHOLAR_API_KEY", $SEMANTIC_SCHOLAR_API_KEY, "User")
        Write-Host "✅ SEMANTIC_SCHOLAR_API_KEY 已设置" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "✅ 环境变量设置完成！" -ForegroundColor Green
    Write-Host ""
    Write-Host "注意：" -ForegroundColor Yellow
    Write-Host "1. 环境变量将在下次启动新的PowerShell时生效" -ForegroundColor Yellow
    Write-Host "2. 如果要在当前会话中立即使用，请运行以下命令：" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "当前会话设置命令：" -ForegroundColor Cyan
    Write-Host "`$env:DEEPSEEK_API_KEY = '$DEEPSEEK_API_KEY'" -ForegroundColor White
    
    if ($OPENAI_API_KEY) {
        Write-Host "`$env:OPENAI_API_KEY = '$OPENAI_API_KEY'" -ForegroundColor White
    }
    
    if ($SERP_API_KEY) {
        Write-Host "`$env:SERP_API_KEY = '$SERP_API_KEY'" -ForegroundColor White
    }
    if ($RXN4CHEM_API_KEY) {
        Write-Host "`$env:RXN4CHEM_API_KEY = '$RXN4CHEM_API_KEY'" -ForegroundColor White
    }
    if ($CHEMSPACE_API_KEY) {
        Write-Host "`$env:CHEMSPACE_API_KEY = '$CHEMSPACE_API_KEY'" -ForegroundColor White
    }
    if ($SEMANTIC_SCHOLAR_API_KEY) {
        Write-Host "`$env:SEMANTIC_SCHOLAR_API_KEY = '$SEMANTIC_SCHOLAR_API_KEY'" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "现在可以运行 python start_server.py 启动服务器了！" -ForegroundColor Green
    
} catch {
    Write-Host "❌ 设置环境变量时出错: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Read-Host "按任意键退出" 