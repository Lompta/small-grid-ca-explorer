import pytest
import numpy as np
from src.rule import Rule

def test_rule_initialization():
    rule = Rule([2, 3])
    np.testing.assert_array_equal(rule.birth_conditions, np.array([2, 3]))

def test_invalid_rule():
    with pytest.raises(ValueError):
        Rule([9])  # Invalid neighbor count
    with pytest.raises(ValueError):
        Rule([-1])  # Invalid neighbor count

def test_rule_application():
    rule = Rule([2, 3])
    neighbor_counts = np.array([
        [1, 2, 3],
        [4, 2, 3],
        [0, 8, 5]
    ])
    expected = np.array([
        [0, 1, 1],
        [0, 1, 1],
        [0, 0, 0]
    ])
    result = rule.apply(neighbor_counts)
    np.testing.assert_array_equal(result, expected)

def test_empty_rule():
    """Test a rule where no cells survive"""
    rule = Rule([])
    neighbor_counts = np.ones((3, 3))
    expected = np.zeros((3, 3))
    result = rule.apply(neighbor_counts)
    np.testing.assert_array_equal(result, expected)

def test_full_rule():
    """Test a rule where all cells survive"""
    rule = Rule(list(range(9)))  # 0-8 neighbors all result in live cells
    neighbor_counts = np.ones((3, 3))
    expected = np.ones((3, 3))
    result = rule.apply(neighbor_counts)
    np.testing.assert_array_equal(result, expected) 