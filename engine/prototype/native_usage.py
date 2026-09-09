"""Native receipt checks; optional missing measurements remain unknown."""
FIELDS=('input_tokens','output_tokens','cached_input_tokens','cache_write_input_tokens','reasoning_output_tokens')


def aggregate(usages):
    if not usages:raise ValueError('No native usage receipts')
    for usage in usages:
        if not isinstance(usage,dict):raise ValueError('Usage receipt required')
        for key in FIELDS:
            value=usage.get(key)
            if value is None:
                if key in FIELDS[:2]:raise ValueError('Missing native input/output measurement')
            elif type(value) is not int or value<0:raise ValueError('Invalid native token count')
    return {key:None if any(u.get(key) is None for u in usages) else sum(u[key] for u in usages) for key in FIELDS}


def validate_resume(status,model,prompt,stored_prompt):
    if status.get('state')!='completed' or status.get('exit_code')!=0:
        raise ValueError('Receipt is not completed successfully')
    if status.get('model')!=model or status.get('effort')!='high':raise ValueError('Model/effort mismatch')
    if prompt!=stored_prompt:raise ValueError('Prompt mismatch')
    return aggregate([status.get('usage')])
