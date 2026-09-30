"""Comandos del módulo 1: Archivos. DUEÑO: Angel Torres

Estos comandos ya están conectados; lo que falta es LinkedList y FileManager.
"""
from __future__ import annotations

import os

from synthetix.commands.utils import CommandUtils
from synthetix.core.command import Command
from synthetix.core.command_args import CommandArgs
from synthetix.core.command_registry import CommandRegistry
from synthetix.files.backup_manager import BackupManager


class NewCommand(Command):
    name = "new"
    usage = "new <nombre_archivo> [contenido]"
    description = "Crea un archivo en memoria y lo activa"
    min_args = 1

    def execute(self, args, ctx) -> None:
        initial = CommandArgs.unescape(args.rest(2))
        if not initial:
            initial = f"# {args[1]}\n"
        elif not initial.endswith("\n"):
            initial += "\n"
        file = ctx.files.create(args[1], initial)
        print(f"Archivo creado: [{file.id}] {file.name} (ahora es el activo)")


class ListCommand(Command):
    name = "list"
    usage = "list"
    description = "Lista los archivos abiertos"

    def execute(self, args, ctx) -> None:
        if ctx.files.count() == 0:
            print("No hay archivos abiertos. Usa 'new <nombre>'.")
            return
        active = ctx.files.active
        print(f"\033[96mArchivos abiertos ({ctx.files.count()}):\033[0m")
        for position, file in enumerate(ctx.files, start=1):
            marca = "\033[92m  * \033[0m" if file is active else "    "
            estado = "\033[93m, sin respaldar\033[0m" if file.modified else ""
            activo = "\033[92m  (activo)\033[0m" if file is active else ""
            print(f"{marca}{position}. [\033[90mid {file.id}\033[0m] \033[97m{file.name}\033[0m  - "
                  f"\033[94m{file.line_count()} líneas\033[0m{estado}{activo}")


class SwitchCommand(Command):
    name = "switch"
    usage = "switch <id/nombre>"
    description = "Cambia el archivo activo"
    min_args = 1

    def execute(self, args, ctx) -> None:
        if not ctx.files.switch_to(args[1]):
            raise RuntimeError(f"No existe el archivo '{args[1]}'")
        print(f"Archivo activo: {ctx.files.active.name}")


class DeleteCommand(Command):
    name = "delete"
    usage = "delete <id/nombre>"
    description = "Elimina un archivo y libera sus nodos"
    min_args = 1

    def execute(self, args, ctx) -> None:
        file = ctx.files.find(args[1])
        if file is None:
            raise RuntimeError(f"No existe el archivo '{args[1]}'")
        name = file.name
        if file.modified:
            path = BackupManager.backup(file, ctx.config.backup_dir)
            print(f"Respaldo automático antes de eliminar: {path}")
        ctx.files.remove(args[1])
        print(f"Archivo eliminado: {name}")


class ShowCommand(Command):
    name = "show"
    usage = "show"
    description = "Muestra el código activo con números de línea"

    def execute(self, args, ctx) -> None:
        file = CommandUtils.active_file(ctx)
        lines = file.lines()
        print(f"\033[96m--- {file.name} ({len(lines)} líneas) ---\033[0m")
        for number, text in enumerate(lines, start=1):
            print(f"\033[92m{number:>4} |\033[0m \033[97m{text}\033[0m")


class WriteCommand(Command):
    name = "write"
    usage = "write"
    description = "Reescribe el archivo activo (terminar con una línea '.')"

    def execute(self, args, ctx) -> None:
        file = CommandUtils.active_file(ctx)
        print(f"Escribe el nuevo contenido de {file.name}. Termina con una línea que solo tenga '.'")
        content = ""
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line.rstrip("\r") == ".":
                break
            content += line.rstrip("\r") + "\n"
        file.apply_edit(content)
        print(f"Contenido actualizado ({file.line_count()} líneas) "
              f"{CommandUtils.history_summary(file)}")


class AppendCommand(Command):
    name = "append"
    usage = "append <texto>"
    description = "Agrega una línea al final"

    def execute(self, args, ctx) -> None:
        file = CommandUtils.active_file(ctx)
        file.append_line(args.rest(1))
        print(f"Línea agregada {CommandUtils.history_summary(file)}")


class InsertCommand(Command):
    name = "insert"
    usage = "insert <línea> <texto>"
    description = "Inserta una línea en la posición dada"
    min_args = 1

    def execute(self, args, ctx) -> None:
        file = CommandUtils.active_file(ctx)
        file.insert_line(CommandUtils.parse_line_number(args[1]), args.rest(2))
        print(f"Línea insertada {CommandUtils.history_summary(file)}")


class ReplaceCommand(Command):
    name = "replace"
    usage = "replace <línea> <texto>"
    description = "Reemplaza el texto de una línea"
    min_args = 1

    def execute(self, args, ctx) -> None:
        file = CommandUtils.active_file(ctx)
        file.replace_line(CommandUtils.parse_line_number(args[1]), args.rest(2))
        print(f"Línea reemplazada {CommandUtils.history_summary(file)}")


class RemoveLineCommand(Command):
    name = "remove"
    usage = "remove <línea>"
    description = "Borra una línea del archivo activo"
    min_args = 1

    def execute(self, args, ctx) -> None:
        file = CommandUtils.active_file(ctx)
        file.remove_line(CommandUtils.parse_line_number(args[1]))
        print(f"Línea borrada {CommandUtils.history_summary(file)}")


class LoadCommand(Command):
    name = "load"
    usage = "load <ruta_en_disco>"
    description = "Abre un archivo del disco en memoria"
    min_args = 1

    def execute(self, args, ctx) -> None:
        path = args.rest(1)
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            raise RuntimeError(f"No se encontró el archivo '{path}' en el disco") from None
        file = ctx.files.create(os.path.basename(path), content)
        print(f"Cargado [{file.id}] {file.name} ({file.line_count()} líneas)")


class SaveCommand(Command):
    name = "save"
    usage = "save"
    description = "Guarda un respaldo en la carpeta de config.json"

    def execute(self, args, ctx) -> None:
        file = CommandUtils.active_file(ctx)
        path = BackupManager.backup(file, ctx.config.backup_dir)
        file.mark_saved()
        ctx.logger.info(f"Respaldo creado: {path}")
        print(f"Respaldo guardado en {path}")


class FileCommandModule:
    @staticmethod
    def register_into(registry: CommandRegistry) -> None:
        for command in (NewCommand(), ListCommand(), SwitchCommand(), DeleteCommand(),
                        ShowCommand(), WriteCommand(), AppendCommand(), InsertCommand(),
                        ReplaceCommand(), RemoveLineCommand(), LoadCommand(), SaveCommand()):
            registry.add(command)
