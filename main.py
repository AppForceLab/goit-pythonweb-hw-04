import asyncio
import aiofiles
import shutil
import argparse
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


async def ensure_dir_exists(directory: Path):
    """Асинхронно создаёт директорию, если она не существует."""
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)


async def copy_file(source: Path, destination: Path):
    """Асинхронно копирует файл в указанную директорию."""
    try:
        await ensure_dir_exists(destination.parent)
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, shutil.copy2, source, destination)
        logging.info(f"Копирован файл: {source} -> {destination}")
    except Exception as e:
        logging.error(f"Ошибка при копировании {source}: {e}")


async def read_folder(source_folder: Path, output_folder: Path):
    """Асинхронно читает файлы из исходной папки и распределяет их по подкаталогам в целевой папке."""
    tasks = []
    for file in source_folder.rglob("*.*"):  # Рекурсивный поиск файлов
        if file.is_file():
            extension = file.suffix.lstrip(".") or "no_extension"
            destination_folder = output_folder / extension
            destination_file = destination_folder / file.name
            tasks.append(copy_file(file, destination_file))
    await asyncio.gather(*tasks)


async def main():
    parser = argparse.ArgumentParser(description="Асинхронное распределение файлов по расширениям.")
    parser.add_argument("source", type=str, help="Путь к исходной папке")
    parser.add_argument("output", type=str, help="Путь к папке назначения")
    args = parser.parse_args()

    source_folder = Path(args.source).resolve()
    output_folder = Path(args.output).resolve()

    if not source_folder.exists() or not source_folder.is_dir():
        logging.error("Исходная папка не существует или не является директорией.")
        return

    await read_folder(source_folder, output_folder)
    logging.info("Файлы успешно распределены.")


if __name__ == "__main__":
    asyncio.run(main())
