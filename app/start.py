#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Chemistry Agent 快速启动脚本
@Time    : 2025/1/27
@Author  : JunYU
@File    : start.py
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    # 导入并运行主启动脚本
    from run_server import main
    main() 