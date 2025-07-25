import pytest
from app.core.tools.reactions import RXNPredictLocal, RXNRetrosynthesisLocal
from app.core.tools.rxn4chem import RXNPredict, RXNRetrosynthesis

# 你可以根据实际API key进行配置
DUMMY_RXN4CHEM_API_KEY = "apk-3bb4cda224fdbaf50d97efe2114727b19c35ff13e487c3307d37d88b35f282ea"
DUMMY_OPENAI_API_KEY = "test_key"

# 测试分子
ETHANOL_SMILES = "CCO"
BENZALDEHYDE_SMILES = "O=CC1=CC=CC=C1"


def test_rxnpredictlocal_valid():
    tool = RXNPredictLocal()
    # 这里假设本地服务可用，否则只测试接口不报错
    result = tool._run(f"{ETHANOL_SMILES}.{ETHANOL_SMILES}")
    print("[test_rxnpredictlocal_valid] result:", result)
    assert isinstance(result, str)


def test_rxnpredictlocal_invalid():
    tool = RXNPredictLocal()
    result = tool._run("not_a_smiles")
    print("[test_rxnpredictlocal_invalid] result:", result)
    assert result == "Incorrect input."


def test_rxnretrosynthesislocal_valid():
    tool = RXNRetrosynthesisLocal()
    # 这里只测试接口不报错
    result = tool._run(ETHANOL_SMILES)
    print("[test_rxnretrosynthesislocal_valid] result:", result)
    assert isinstance(result, str)


def test_rxnretrosynthesislocal_invalid():
    tool = RXNRetrosynthesisLocal()
    result = tool._run("not_a_smiles")
    print("[test_rxnretrosynthesislocal_invalid] result:", result)
    assert result == "Incorrect input."


def test_rxnpredict_api_keyerror(monkeypatch):
    """测试RXNPredict遇到无prediction_id时的异常处理"""
    class DummyRXN4Chem:
        def predict_reaction(self, reactants):
            return {"status": 429, "message": "Too fast requests"}
    tool = RXNPredict(DUMMY_RXN4CHEM_API_KEY)
    tool.rxn4chem = DummyRXN4Chem()
    try:
        tool._run(ETHANOL_SMILES)
    except KeyError as e:
        print("[test_rxnpredict_api_keyerror] Caught KeyError as expected:", e)
        raise


def test_rxnretrosynthesis_api_keyerror(monkeypatch):
    """测试RXNRetrosynthesis遇到无prediction_id时的异常处理"""
    class DummyRXN4Chem:
        def predict_automatic_retrosynthesis(self, product, **kwargs):
            return {"status": 429, "message": "Too fast requests"}
    tool = RXNRetrosynthesis(DUMMY_RXN4CHEM_API_KEY, DUMMY_OPENAI_API_KEY)
    tool.rxn4chem = DummyRXN4Chem()
    try:
        tool._run(ETHANOL_SMILES)
    except KeyError as e:
        print("[test_rxnretrosynthesis_api_keyerror] Caught KeyError as expected:", e)
        raise 