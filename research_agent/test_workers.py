from workers.search_worker import SearchWorker
from workers.file_worker import FileWorker

search = SearchWorker()
file = FileWorker()

print(search.process("Who invented Python?"))
print("-" * 50)
print(file.process("Read python.pdf"))