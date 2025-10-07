from django.core.management.base import BaseCommand
from ...models import Vessel
import threading
from django.db import transaction


class Command(BaseCommand):
    help = "Simulate condition when withdrawing refrigerant from a vessel."

    def handle(self, *args, **kwargs):
        Vessel.objects.create(name="Test Vessel", content=50.0)
        self.stdout.write("Simulating condition...")
        self.run_simulation()

    def run_simulation(self):
        barrier = threading.Barrier(2)

        def user1():
            barrier.wait()
            with transaction.atomic():
                vessel = Vessel.objects.select_for_update().get(id=1) # lock vessel row during runtime, prevent concurrent changes
                vessel.content = max(vessel.content - 10.0, 0) # avoid negative value
                vessel.save()
        print("Thread 1 passed successfully!") # check if thread 1 ends successfully

        def user2():
            barrier.wait()
            with transaction.atomic():
                vessel = Vessel.objects.select_for_update().get(id=1) # lock vessel row during runtime, prevent concurrent changes
                vessel.content = max(vessel.content - 10.0, 0) # avoid negative value
                vessel.save()
        print("Thread 2 passed successfully!") # check if thread 2 ends successfully

        t1 = threading.Thread(target=user1)
        t2 = threading.Thread(target=user2)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        vessel = Vessel.objects.get(id=1)
        self.stdout.write(f"Remaining content: {vessel.content} kg")
