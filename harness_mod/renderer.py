from schemas import GeneratedJUnitTest



def render_junit_java(result: GeneratedJUnitTest) -> str:
    lines: list[str] = []

    if result.package_name:
        lines.append(f'package {result.package_name};')
        lines.append('')

    for imp in result.imports:
        lines.append(f'import {imp};')
    lines.append('')

    lines.append(f'class {result.class_name} ' + '{')

    for field in result.setup_fields:
        lines.append(f'    {field}')
    lines.append('')

    lines.append('    @BeforeEach')
    lines.append('    void setUp() {')
    for line in result.setup_method.splitlines():
        lines.append(f'        {line}')
    lines.append('    }')
    lines.append('')

    for method in result.test_methods:
        for line in method.code.splitlines():
            lines.append(f'    {line}')
        lines.append('')

    lines.append('}')
    return '\n'.join(lines)
