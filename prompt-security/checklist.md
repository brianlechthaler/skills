# Prompt Security Checklist

Use with [SKILL.md](SKILL.md) during review or before shipping system prompt changes.

## Confidentiality

- [ ] Model instructed never to reveal, quote, paraphrase, encode, or reconstruct system instructions
- [ ] Indirect extraction covered (summarize, translate, JSON dump, "text above", debugging pretext)
- [ ] Refusal response is short and offers legitimate help
- [ ] Prompt does not instruct the model to describe or enumerate its own rules to users

## Instruction hierarchy

- [ ] System instructions ranked above user messages
- [ ] Developer/operator channel defined if the product has one
- [ ] Tool, file, web, and third-party content marked untrusted
- [ ] Conflict resolution rule stated explicitly

## Injection and override resistance

- [ ] "Ignore previous instructions" / jailbreak patterns addressed
- [ ] Role-play and persona-switch attacks addressed
- [ ] Instructions embedded in documents or tool output do not override policy
- [ ] Coding agents: no exfiltration of secrets, env, or unrelated repos

## Secrets and sensitive data

- [ ] No API keys, passwords, or tokens in prompt text
- [ ] No private URLs, internal hostnames, or VPN paths in prompt text
- [ ] Examples use placeholders (`<API_KEY>`, `example.com`)
- [ ] Logging/support implications considered (prompts may be stored)

## Scope and behavior

- [ ] Allowed capabilities and forbidden actions listed
- [ ] Refusal patterns paired with safe alternatives where possible
- [ ] Out-of-scope requests handled without leaking policy detail
- [ ] Harmful or policy-violating requests refused consistently

## Testing

- [ ] Direct leak request tested
- [ ] Indirect leak request tested (summarize your rules)
- [ ] Encoding/obfuscation request tested
- [ ] Fake tool-output injection tested (if applicable)
- [ ] Malicious content in uploaded file tested (if applicable)

## Documentation

- [ ] Change summary lists added clauses and removed risks
- [ ] Residual platform limitations noted (if any)
- [ ] Operator runbook updated if secrets or config moved out of prompt
