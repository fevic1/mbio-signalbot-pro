from pathlib import Path


class SkillTemplateEngine:


    def __init__(
        self,
        template_dir="aios/skills/templates",
    ):

        self.template_dir = Path(
            template_dir
        )


    def load_template(
        self,
        name="SKILL.md.tmpl",
    ):

        path = (
            self.template_dir
            /
            name
        )

        if not path.exists():
            raise FileNotFoundError(
                path
            )

        return path.read_text()


    def render(
        self,
        values,
    ):

        template = self.load_template()

        output = template

        for key, value in values.items():

            output = output.replace(
                "{{" + key + "}}",
                str(value)
            )

        return output


    def generate(
        self,
        values,
        output_path,
    ):

        content = self.render(
            values
        )

        path = Path(
            output_path
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            content
        )

        return path
