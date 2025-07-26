import ast
import os
import pytest
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 设置代理
os.environ["http_proxy"] = "http://127.0.0.1:7897"
os.environ["https_proxy"] = "http://127.0.0.1:7897"

# 加载环境变量
load_dotenv()

# 导入工具
from app.core.tools.search import PatentCheck, Scholar2ResultLLM
from app.core.utils import split_smiles


@pytest.fixture
def questions():
    qs = [
        "What are the effects of norhalichondrin B in mammals?",
    ]
    return qs[0]


@pytest.mark.skip(reason="This requires an api call")
def test_litsearch(questions):
    """测试文献搜索功能"""
    llm = ChatOpenAI(
        model_name="deepseek-chat",
        openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
        openai_api_base="https://api.deepseek.com/v1"
    )

    searchtool = Scholar2ResultLLM(
        llm=llm,
        openai_api_key=os.getenv("DEEPSEEK_API_KEY"),
        semantic_scholar_api_key=os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    )
    for q in questions:
        ans = searchtool._run(q)
        assert isinstance(ans, str)
        assert len(ans) > 0
    if os.path.exists("query"):
        import shutil
        shutil.rmtree("query")


@pytest.fixture
def molset1():
    return "O=C1N(C)C(C2=C(N=CN2C)N1C)=O.CC(C)c1ccccc1"


@pytest.fixture
def singlemol():
    return "O=C1N(C)C(C2=C(N=CN2C)N1C)=O"


@pytest.fixture
def single_iupac():
    # Test with a molecule with iupac name
    return "4-(4-hydroxyphenyl)butan-2-one"


@pytest.fixture
def choline():
    # Test with a molecule in clintox
    return "CCCCCCCCC[NH+]1C[C@@H]([C@H]([C@@H]([C@H]1CO)O)O)O"


@pytest.fixture
def patentcheck():
    return PatentCheck()


def test_patentcheck(singlemol, patentcheck):
    """测试专利检查功能"""
    patented = patentcheck._run(singlemol)
    patented = ast.literal_eval(patented)
    assert len(patented) == 1
    assert patented[singlemol] == "Patented"


def test_patentcheck_molset(molset1, patentcheck):
    """测试多个分子的专利检查"""
    patented = patentcheck._run(molset1)
    patented = ast.literal_eval(patented)
    mols = split_smiles(molset1)
    assert len(patented) == len(mols)
    assert patented[mols[0]] == "Patented"
    assert patented[mols[1]] == "Novel"


def test_patentcheck_iupac(single_iupac, patentcheck):
    """测试IUPAC名称的专利检查"""
    patented = patentcheck._run(single_iupac)
    assert patented == "Invalid SMILES string"


def test_patentcheck_not(choline, patentcheck):
    """测试非专利分子的检查"""
    patented = patentcheck._run(choline)
    patented = ast.literal_eval(patented)
    assert len(patented) == 1
    assert patented[choline] == "Novel"
