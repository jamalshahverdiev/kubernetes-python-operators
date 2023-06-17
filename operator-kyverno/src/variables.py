class Settings:
    kyverno_namespace = 'kyverno'
    group = "kyverno.io"
    version = 'v1'
    plural = "policies"
    crd_group_name = 'kyverno.opso.info'
    crd_kind_name = 'policywriters'
    template_file = 'templates/policy-file.json'    
