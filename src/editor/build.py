import os.path
import shutil
from commons import ed_logging


class BuildScript:
    """This class is responsible for building your project into the final runtime executable or
    optionally output a without editor panda3D program in which case you are responsible for building the
    final runtime executable yourself."""

    @staticmethod
    def run(project_path, output_dir, build_name="PandaGame", build_target=None, build_executable=False,
            ignore_extensions=None):
        """
        :param project_path:
        :param output_dir:
        :param build_name:
        :param build_target:
        :param build_executable:
        :param ignore_extensions:
        :return:
        """

        if ignore_extensions is None:
            ignore_extensions = [".pyc"]

        if os.path.exists(output_dir):
            if len(os.listdir(output_dir)) > 0:
                # ed_logging.log_exception("Build failed, target directory is not empty!")
                return
        else:
            os.mkdir(output_dir)

        def ignore_callable(*args, **kwargs):
            files = []
            for file in args[1]:
                if os.path.isfile(os.path.join(args[0], file)):
                    if os.path.splitext(file)[-1] in ignore_extensions:
                        files.append(file)

            files.append("__pycache__")
            return files

        output_dir = os.path.join(output_dir, "resources")
        shutil.copytree(project_path, output_dir, symlinks=False, ignore=ignore_callable, ignore_dangling_symlinks=True)


