from django.core.management.base import BaseCommand
from ...models import Vessel
import threading
from django.db import transaction


class Command(BaseCommand):
    help = "Simulate condition when withdrawing refrigerant from a vessel."

    def handle(self, *args, **kwargs):
        Vessel.objects.all().delete() # delete garbage
        vessel = Vessel.objects.create(name="Test Vessel", content=50.0)
        vessel_id = vessel.id # avoid hardcoded vessel id (error: refrigerant.models.Vessel.DoesNotExist: Vessel matching query does not exist. ), auto-increment in db (rows probably deleted by line 11)
        self.stdout.write("Simulating condition...")
        self.run_simulation(vessel_id)

    def run_simulation(self, vessel_id):
        barrier = threading.Barrier(2)

        def withdraw(amount, thread_name): # use withdraw function instead of user 1/2 functions to improve the code
            barrier.wait()
            with transaction.atomic(): # db transaction for safety
                vessel = Vessel.objects.select_for_update().get(id=vessel_id) # lock vessel row during runtime, prevent concurrent changes
                if vessel.content <= 0: # avoid negative value with if check
                    print(f"{thread_name}: Vessel is empty, cannot withdraw!")
                    return
                vessel.content = max(vessel.content - amount, 0)
                vessel.save()
                print(f"{thread_name}: Successfully withdrew {amount} kg. Remaining: {vessel.content} kg")

        t1 = threading.Thread(target=withdraw, args=(10.0, "Thread/User 1"))
        t2 = threading.Thread(target=withdraw, args=(10.0, "Thread/User 2"))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        vessel = Vessel.objects.get(id=vessel_id)
        self.stdout.write(f"Simulation complete. Remaining content: {vessel.content} kg")
