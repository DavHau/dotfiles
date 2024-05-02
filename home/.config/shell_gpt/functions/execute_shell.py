import subprocess

from instructor import OpenAISchema
from pydantic import Field


class Function(OpenAISchema):
    """
    Executes a shell command and returns the output (result).
    """

    shell_command: str = Field(
        ...,
        example="ls -la",
        descriptions="Shell command to execute.",
    )

    class Config:
        title = "execute_shell_command"

    @classmethod
    def execute(cls: object, shell_command: str) -> str:
        yes_no = input(f"Execute shell command: '{shell_command}'? (yes/no): ")
        if yes_no.lower() != "yes":
            return "Aborted."

        process = subprocess.Popen(
            shell_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT # noqa: S602
        )
        output, _ = process.communicate()
        exit_code = process.returncode
        return f"Exit code: {exit_code}, Output:\n{output.decode()}"
