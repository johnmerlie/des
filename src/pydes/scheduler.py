from pydes.core import Field, Immutable
from pydes.model import Model
from pydes.utils import MapQueue


class Scheduler(Immutable):
    queue: MapQueue[Model] = Field(default_factory=MapQueue)

    def schedule(self, model: Model):
        if result := self.queue.push(model, model.time.next):
            # model added successfully
            return result
        else:
            # model needs to be updated
            self.queue.update(model, model.time.next)

    def deschedule(self, model: Model):
        return self.queue.remove(model)
