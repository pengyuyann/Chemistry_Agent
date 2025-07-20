@echo off
chcp 65001 >nul
echo ========================================
echo    Chemistry Agent API 环境变量设置
echo ========================================
echo.

echo 请按照提示输入你的API密钥：
echo.

set /p DEEPSEEK_API_KEY="请输入你的 DeepSeek API Key: "
set /p OPENAI_API_KEY="请输入你的 OpenAI API Key (可选，直接回车跳过): "
set /p SERP_API_KEY="请输入你的 SERP API Key (可选，直接回车跳过): "
set /p RXN4CHEM_API_KEY="请输入你的 RXN4Chem API Key (可选，直接回车跳过): "
set /p CHEMSPACE_API_KEY="请输入你的 ChemSpace API Key (可选，直接回车跳过): "
set /p SEMANTIC_SCHOLAR_API_KEY="请输入你的 Semantic Scholar API Key (可选，直接回车跳过): "

echo.
echo 正在设置环境变量...

:: 设置环境变量
setx DEEPSEEK_API_KEY "%DEEPSEEK_API_KEY%"

if not "%SERP_API_KEY%"=="" (
    setx SERP_API_KEY "%SERP_API_KEY%"
    echo ✅ SERP_API_KEY 已设置
)

if not "%RXN4CHEM_API_KEY%"=="" (
    setx RXN4CHEM_API_KEY "%RXN4CHEM_API_KEY%"
    echo ✅ RXN4CHEM_API_KEY 已设置
)

if not "%CHEMSPACE_API_KEY%"=="" (
    setx CHEMSPACE_API_KEY "%CHEMSPACE_API_KEY%"
    echo ✅ CHEMSPACE_API_KEY 已设置
)

if not "%SEMANTIC_SCHOLAR_API_KEY%"=="" (
    setx SEMANTIC_SCHOLAR_API_KEY "%SEMANTIC_SCHOLAR_API_KEY%"
    echo ✅ SEMANTIC_SCHOLAR_API_KEY 已设置
)

echo.
echo ✅ 环境变量设置完成！
echo.
echo 注意：
echo 1. 环境变量将在下次启动新的命令提示符时生效
echo 2. 如果要在当前会话中立即使用，请运行以下命令：
echo.
echo 当前会话设置命令：
echo set DEEPSEEK_API_KEY=%DEEPSEEK_API_KEY%
if not "%OPENAI_API_KEY%"=="" echo set OPENAI_API_KEY=%OPENAI_API_KEY%
if not "%SERP_API_KEY%"=="" echo set SERP_API_KEY=%SERP_API_KEY%
if not "%RXN4CHEM_API_KEY%"=="" echo set RXN4CHEM_API_KEY=%RXN4CHEM_API_KEY%
if not "%CHEMSPACE_API_KEY%"=="" echo set CHEMSPACE_API_KEY=%CHEMSPACE_API_KEY%
if not "%SEMANTIC_SCHOLAR_API_KEY%"=="" echo set SEMANTIC_SCHOLAR_API_KEY=%SEMANTIC_SCHOLAR_API_KEY%
echo.
echo 现在可以运行 python start_server.py 启动服务器了！
echo.
pause 