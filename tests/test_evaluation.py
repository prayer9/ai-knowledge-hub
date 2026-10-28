from scripts.evaluate_retrieval import run

def test_evaluation_smoke():
    result=run()
    assert result["questions"]==20
    assert 0 <= result["source_hit_at_3"] <= 1
