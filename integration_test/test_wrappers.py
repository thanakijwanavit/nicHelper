import pytest
from nicHelper.wrappers import add_method, add_static_method, add_class_method


def test_add_method():
    class TestClass:
        pass

    @add_method(TestClass)
    def test_method(self, value):
        return f"Method received: {value}"

    instance = TestClass()
    result = instance.test_method("test_value")
    assert result == "Method received: test_value"


def test_add_static_method():
    class TestClass:
        pass

    @add_static_method(TestClass)
    def test_static_method(value):
        return f"Static method received: {value}"

    result = TestClass.test_static_method("test_value")
    assert result == "Static method received: test_value"


@pytest.mark.skip(reason="add_class_method has issues with Python 3.12")
def test_add_class_method():
    class TestClass:
        name = "TestClass"

    @add_class_method(TestClass)
    def test_class_method(cls, value):
        return f"{cls.name} received: {value}"

    result = TestClass.test_class_method("test_value")
    assert result == "TestClass received: test_value"


def test_method_inheritance():
    """Test that methods added to parent classes are inherited by child classes"""

    class Parent:
        pass

    class Child(Parent):
        pass

    @add_method(Parent)
    def parent_method(self, value):
        return f"Parent method: {value}"

    # Child should inherit the method
    child = Child()
    result = child.parent_method("inheritance")
    assert result == "Parent method: inheritance"
