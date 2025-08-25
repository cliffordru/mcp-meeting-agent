# Commit Message Template

## Type
Choose one of the following types:

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools and libraries such as documentation generation

## Scope (optional)
<scope>

**Examples:**
- `feat(api): add new endpoint for user preferences`
- `fix(service): resolve timeout in GitHub trending service`
- `refactor(agent): remove unused meeting_info parameter`

## Description
<description>

**Examples:**
- `feat: add user authentication system`
- `fix: resolve API timeout issue in GitHub trending service`
- `refactor: remove unused meeting_info parameter from planner agent`
- `docs: update README with new project structure`
- `test: add coverage for repository formatter`
- `chore: update dependencies to latest versions`

## Breaking Changes (optional)
If this commit introduces breaking changes, describe them here:

**Before:**
```python
def prepare_meeting(meeting_info: str = "") -> str:
```

**After:**
```python
def prepare_meeting() -> str:
```

## Description

[Provide a more detailed description of the changes.]

## Related Issues

- Closes #issue_number or issue description
- Related to #issue_number or issue description

## Checklist

- [ ] I have tested these changes locally.
- [ ] I have updated the documentation.
- [ ] My commits follow the project's commit message format.
- [ ] I have added tests for new functionality (if applicable).
- [ ] I have checked that my changes don't break existing functionality.
