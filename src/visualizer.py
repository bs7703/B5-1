from typing import Any
from dataclasses import is_dataclass, fields

class Visualizer:
     
    @staticmethod
    def _ref(value: Any) -> str:
        return f"<{type(value).__name__}@{id(value):x}>"

    @staticmethod
    def _format(value: Any) -> str:
        if value is None or isinstance(value, (str, int, float, bool)):
            return repr(value)

        if isinstance(value, dict):
            return repr(value)

        if is_dataclass(value) and not isinstance(value, type):
            data = {}

            for field in fields(value):
                field_value = getattr(value, field.name)

                if field_value is None or isinstance(field_value, (str, int, float, bool, dict)):
                    data[field.name] = field_value
                else:
                    data[field.name] = Visualizer._ref(field_value)

            return repr(data)

        return Visualizer._ref(value)
    @staticmethod
    def heap(heap: Any) -> str:
        data = heap._data

        if not data:
            return "<empty heap>"

        lines: list[str] = []

        def build(
            index: int,
            prefix: str = "",
            is_tail: bool = True,
        ) -> None:

            if index >= len(data):
                return

            right = index * 2 + 2
            left = index * 2 + 1

            if right < len(data):
                build(
                    right,
                    prefix + ("│   " if is_tail else "    "),
                    False,
                )

            lines.append(
                prefix
                + ("└── " if is_tail else "┌── ")
                + f"[{index}] {data[index]!r}"
            )

            if left < len(data):
                build(
                    left,
                    prefix + ("    " if is_tail else "│   "),
                    True,
                )

        build(0)

        return "\n".join(lines)

    @staticmethod
    def hashmap(hashmap: Any, show_empty: bool = False, empty_limit: int = 32) -> str:
        data = hashmap._buckets

        if not data:
            return "<empty hashmap>"

        lines: list[str] = []
        show_none = show_empty or len(data) <= empty_limit

        for index, node in enumerate(data):
            if node is None:
                if show_none:
                    lines.append(f"[{index:>3}] -> None")
                continue

            chain: list[str] = []
            visited: set[int] = set()
            current = node

            while current is not None:
                if id(current) in visited:
                    chain.append("<CYCLE>")
                    break

                visited.add(id(current))

                key = Visualizer._format(current.key)
                data = Visualizer._format(current.data)

                chain.append(f"({key}: {data})")
                current = current.next

            lines.append(f"[{index:>3}] -> " + " -> ".join(chain) + " -> None")

        return "\n".join(lines)
    @staticmethod
    def doubly_linked_list(
        linked_list: Any,
        value_attr: str = "data",
    ) -> str:

        node = linked_list.head

        if node is None:
            return "HEAD ⇄ None ⇄ TAIL"

        values: list[str] = []
        visited: set[int] = set()

        while node is not None:

            if id(node) in visited:
                values.append("<CYCLE>")
                break

            visited.add(id(node))

            value = getattr(node, value_attr, node)

            values.append(
                f"[{value!r}]"
            )

            node = node.next

        return (
            "HEAD ⇄ "
            + " ⇄ ".join(values)
            + " ⇄ TAIL"
        )