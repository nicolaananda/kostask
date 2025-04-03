import time
import logging
from django.core.management.base import BaseCommand
from tickets.task_manager import TaskManager

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Process tasks from the task queue'

    def add_arguments(self, parser):
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='Run continuously, processing tasks as they come in',
        )
        parser.add_argument(
            '--sleep',
            type=int,
            default=5,
            help='Sleep time between checks when running continuously (in seconds)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Maximum number of tasks to process',
        )

    def handle(self, *args, **options):
        continuous = options['continuous']
        sleep_time = options['sleep']
        limit = options['limit']
        
        processed_count = 0
        
        self.stdout.write(self.style.SUCCESS('Starting task processor'))
        
        try:
            if continuous:
                self.stdout.write(f'Running in continuous mode (sleep: {sleep_time}s)')
                while True:
                    processed = TaskManager.process_next_task()
                    if processed:
                        processed_count += 1
                        self.stdout.write(f'Processed task ({processed_count})')
                        
                        if limit and processed_count >= limit:
                            self.stdout.write(self.style.SUCCESS(f'Reached limit of {limit} tasks. Exiting.'))
                            break
                    else:
                        self.stdout.write('No tasks to process, sleeping...')
                        time.sleep(sleep_time)
            else:
                self.stdout.write('Running in one-off mode')
                while True:
                    processed = TaskManager.process_next_task()
                    if processed:
                        processed_count += 1
                        self.stdout.write(f'Processed task ({processed_count})')
                        
                        if limit and processed_count >= limit:
                            break
                    else:
                        break
                
                self.stdout.write(self.style.SUCCESS(f'Processed {processed_count} tasks'))
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Interrupted by user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            logger.exception('Error in process_tasks command')
            
        self.stdout.write(self.style.SUCCESS(f'Task processor finished. Processed {processed_count} tasks.'))
