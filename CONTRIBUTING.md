# 🤝 Contributing to Manalytics

## Code of Conduct

Be respectful, inclusive, and constructive.

## How to Contribute

### 1. Report Issues

- Use issue templates
- Provide reproduction steps
- Include error logs

### 2. Submit Pull Requests

- Fork repository
- Create feature branch
- Write tests first
- Update documentation
- Submit PR with description

### 3. Development Process

1. Discuss in issue first
2. Get approval on approach
3. Implement with TDD
4. Request review
5. Iterate based on feedback

## Commit Convention

```
type(scope): subject

body

footer
```

**Types**: feat, fix, docs, style, refactor, test, chore

## Quality Standards

- 90%+ test coverage for new code
- All tests passing
- Documentation updated
- No linting errors
- Performance benchmarked

## Règles de style et flake8

- **flake8** est utilisé pour garantir la qualité du code Python.
- **Obligatoire** : Corriger toutes les erreurs sûres (ex : E231, espace manquant après les deux-points).
- **Optionnel** : Les lignes longues (E501) NE SONT PAS BLOQUANTES pour les scripts/outils, afin de préserver la lisibilité et la robustesse.
- Si un hook bloque un commit pour une ligne longue ou une règle non critique, corrigez uniquement si cela ne nuit pas à la lisibilité ou à la logique du script.
- Pour les scripts/outils, la priorité est la robustesse et la clarté, pas la conformité stricte à E501.
