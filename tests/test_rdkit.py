import pytest
from dotenv import load_dotenv

# 设置代理
import os
os.environ["http_proxy"] = "http://127.0.0.1:7897"
os.environ["https_proxy"] = "http://127.0.0.1:7897"

# 加载环境变量
load_dotenv()

# 导入工具
from app.core.tools.rdkit import FuncGroups, MolSimilarity, SMILES2Weight


@pytest.fixture
def singlemol():
    # Single mol
    return "O=C1N(C)C(C2=C(N=CN2C)N1C)=O"


@pytest.fixture
def molset1():
    # Set of mols
    return "O=C1N(C)C(C2=C(N=CN2C)N1C)=O.CC(C)c1ccccc1"


@pytest.fixture
def molset2():
    # Set of mols
    return "O=C1N(C)C(C2=C(N=CN2C)N1C)=O.O=C1N(C)C(C2=C(N=CN2C)N1CCC)=O"


@pytest.fixture
def single_iupac():
    # Test with a molecule with iupac name
    return "4-(4-hydroxyphenyl)butan-2-one"


# MolSimilarity


def test_molsim_1(molset1):
    """测试分子相似性 - 不相似的情况"""
    tool = MolSimilarity()
    assert tool(molset1).endswith("not similar.")


def test_molsim_2(molset2):
    """测试分子相似性 - 相似的情况"""
    tool = MolSimilarity()
    assert tool(molset2).endswith("very similar.")


def test_molsim_same(singlemol):
    """测试相同分子的相似性"""
    tool = MolSimilarity()
    out = tool("{}.{}".format(singlemol, singlemol))
    assert out == "Error: Input Molecules Are Identical"


def test_molsim_badinp(singlemol):
    """测试单个分子的相似性输入"""
    tool = MolSimilarity()
    out = tool(singlemol)
    assert out == "Input error, please input two smiles strings separated by '.'"


def test_molsim_iupac(singlemol, single_iupac):
    """测试IUPAC名称的分子相似性"""
    tool = MolSimilarity()
    out = tool("{}.{}".format(singlemol, single_iupac))
    assert out == "Error: Not a valid SMILES string"


# SMILES2Weight


def test_mw(singlemol):
    """测试分子量计算"""
    tool = SMILES2Weight()
    mw = tool(singlemol)
    assert abs(mw - 194.0) < 1.0


def test_badinp(singlemol):
    """测试无效输入的分子量计算"""
    tool = SMILES2Weight()
    mw = tool(singlemol + "x")
    assert mw == "Invalid SMILES string"


# FuncGroups


def test_fg_single(singlemol):
    """测试单个分子的官能团识别"""
    tool = FuncGroups()
    out = tool(singlemol)
    assert "ketones" in out


def test_fg_iupac(single_iupac):
    """测试IUPAC名称的官能团识别"""
    tool = FuncGroups()
    out = tool(single_iupac)
    assert out == "Wrong argument. Please input a valid molecular SMILES."
