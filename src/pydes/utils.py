import heapq
from collections.abc import Iterable
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True, order=True)
class QueueItem[T]:
    priority: float = field(hash=False)
    value: T = field(hash=True)

    def __hash__(self) -> int:
        return hash(self.value)


class MapQueue[T]:
    heap: list[QueueItem[T]]
    position: dict[T, int]

    def __init__(self, data: Iterable[tuple[float, T]] | None = None):
        if data is None:
            data = []
        self.heap = [QueueItem(*v) for v in data]
        self.position = {}
        self.__heapify()

    def __len__(self):
        return len(self.heap)

    def __heapify(self):
        heapq.heapify(self.heap)
        self.position = {item.value: pos for pos, item in enumerate(self.heap)}
        if len(self.heap) != len(self.position):
            raise ValueError("Duplicate Elements")

    def __set(self, item: QueueItem[T], position: int):
        self.heap[position], self.position[item.value] = item, position

    def __sift_down(self, start_pos: int, pos: int):
        new_item = self.heap[pos]
        while pos > start_pos:
            parent = self.heap[parent_pos := (pos - 1) >> 1]
            if not new_item < parent:
                break
            self.__set(parent, pos)
            pos = parent_pos
        self.__set(new_item, pos)

    def __sift_up(self, pos: int):
        end_pos = len(self.heap)
        new_item = self.heap[pos]
        child_pos = (pos << 1) + 1
        while child_pos < end_pos:
            child = self.heap[child_pos]
            if (right_pos := child_pos + 1) < end_pos:
                right = self.heap[right_pos]
                if not child < right:
                    child, child_pos = right, right_pos
            self.__set(child, pos)
            pos = child_pos
            child_pos = (pos << 1) + 1
        while pos > 0:
            parent = self.heap[parent_pos := (pos - 1) >> 1]
            if not new_item < parent:
                break
            self.__set(parent, pos)
            pos = parent_pos
        self.__set(new_item, pos)

    def push(self, value: T, priority: float):
        if value in self.position:
            return False
        pos = len(self.heap)
        self.heap.append(QueueItem(priority, value))
        self.position[value] = pos
        self.__sift_down(0, pos)
        return True

    def pop(self) -> T:
        del self.position[value := self.heap[0].value]
        if len(self.heap) == 1:
            self.heap.pop()
            return value
        self.__set(self.heap.pop(), 0)
        self.__sift_up(0)
        return value

    def update(self, value: T, new_value: T, priority: float):
        pos = self.position.pop(value)
        self.__set(QueueItem(priority, new_value), pos)
        self.__sift_up(pos)

    def remove(self, value: T):
        if (pos := self.position.pop(value)) == len(self.heap) - 1:
            self.heap.pop()
            return
        self.__set(self.heap.pop(), pos)
        self.__sift_up(pos)
