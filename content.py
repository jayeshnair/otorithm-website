"""
All Otorithm website copy lives here. Edit this file, then run `python3 build.py`.

Plain text fields are HTML-escaped by the builder. Fields named `html` (article bodies)
are inserted as written.
"""

SITE = {
    'name': 'Otorithm',
    'domain': 'https://otorithm.com',
    'legal': 'System One Technologies Private Limited',
    'email': 'contact@otorithm.com',
    'careers_email': 'careers@otorithm.com',
    'city': 'Gurugram, Haryana, India',
    'hours': 'Monday to Friday, 09:30 to 20:30 IST',
    # Set to a form backend URL (Formspree, Basin, your own API) to post the contact form.
    # Left empty, the form composes the message for the visitor to email instead.
    'form_endpoint': '',
    # Home hero video (assets/videos/<file>.mp4 + .jpg, made with tools/prepare_hero_video.py).
    # particles: the cursor-reactive particle logo drawn over the video.
    'hero_video': {'file': 'structure', 'opacity': 1, 'particles': True},
    'tagline': 'An AI-native engineering consultancy. We build, modernize and run production software with senior engineers and AI throughout our delivery.',
}

# ---------------------------------------------------------------------------
# Full-width image bands on the home page (one per main section).
# Put a file in assets/images/ (2400 x 400 works well) and set 'src' to show it;
# with 'src' empty the band shows a placeholder with the suggested subject.
# ---------------------------------------------------------------------------
IMAGES = {
    # pos: which part stays in view when narrow screens crop the band (CSS object-position)
    'home-different': {'src': 'assets/images/home-different.jpg', 'pos': '50% 50%',
                       'alt': 'Silhouette of a person standing beneath a sky full of glowing particles',
                       'hint': 'An engineer reviewing an AI agent\'s pull request'},
    'home-services': {'src': 'assets/images/home-services.jpg', 'pos': '50% 50%',
                      'alt': 'A hand about to launch a blue paper plane against sunlit trees',
                      'hint': 'Architecture session: systems sketched on a whiteboard'},
    'home-engage': {'src': 'assets/images/home-engage.jpg', 'pos': '57% 30%',
                    'alt': 'Two people on sunlit coastal rocks, one sitting on a ledge above the sea',
                    'hint': 'A small team planning around one table'},
    'home-industries': {'src': 'assets/images/home-industries.jpg', 'pos': '6% 50%',
                        'alt': 'A lighthouse lantern overlooking a wide beach and open sea',
                        'hint': 'Operations in motion: payments, logistics, marketplaces'},
    'home-why': {'src': 'assets/images/home-why.jpg', 'pos': '70% 50%', 'alt': '',
                 'hint': 'Engineers at work in the delivery centre, natural light'},
    'home-insights': {'src': 'assets/images/home-insights.jpg', 'pos': '40% 50%',
                      'alt': 'A person in a suit with a glowing wireframe brain in place of a head',
                      'hint': 'Editorial still life: notebook, laptop, sketches'},
}

# ---------------------------------------------------------------------------
# Engagement models (referenced by services)
# ---------------------------------------------------------------------------
MODELS = {
    'sprint': {
        'name': 'Readiness sprint',
        'term': '2 to 3 weeks, fixed fee',
        'what': 'A defined question answered: an assessment, an architecture review or a scored use-case portfolio.',
        'best': 'Deciding what to do next, with evidence.',
    },
    'pilot': {
        'name': 'Pilot to production',
        'term': '4 to 10 weeks, fixed scope',
        'what': 'One use case built on your data and released to real users, against success measures agreed up front.',
        'best': 'Proving value before a larger commitment.',
    },
    'pod': {
        'name': 'Forward-deployed pod',
        'term': 'Monthly',
        'what': 'A small senior team embedded in your business that owns an outcome end to end.',
        'best': 'Problems that cross teams and systems.',
    },
    'extension': {
        'name': 'Team extension',
        'term': 'Monthly, per engineer',
        'what': 'Senior engineers who join your team, work to your plan and report to your leads.',
        'best': 'A clear roadmap that needs more hands.',
    },
    'advisory': {
        'name': 'Embedded advisory',
        'term': 'Monthly, part-time',
        'what': 'A consultant or fractional engineering leader inside your organization a set number of days each month.',
        'best': 'Steering AI and platform decisions.',
    },
}
MODEL_ORDER = ['sprint', 'pilot', 'pod', 'extension', 'advisory']

# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------
SERVICE_GROUPS = [
    ('Build', ['ai-first-engineering', 'platform-engineering']),
    ('Transform', ['legacy-modernization', 'ai-consulting']),
    ('Extend', ['forward-deployed-engineering', 'staff-augmentation']),
]

SERVICES = {
    'ai-first-engineering': {
        'name': 'AI-First Product Engineering',
        'nav': 'Agents, copilots and AI features built to run in production.',
        'short': 'Products designed around models from the first sprint: agents, copilots, retrieval and automated workflows, built with evals, guardrails and cost controls.',
        'start': 'Usually starts with a 2-week discovery',
        'formation': 'ascent',
        'title': 'AI products that hold up in production.',
        'lead': 'We design and build software where models do real work: agents that complete multi-step tasks, copilots inside your product, search over your own knowledge, and workflows that run without manual handoffs. Every feature ships with the evals, guardrails and cost controls it needs to stay reliable after launch.',
        'deliver_title': 'What we build',
        'deliver': [
            ('Agents and agentic workflows', 'Agents that plan, call your systems through typed tools, and hand off to people at the right moments.'),
            ('Copilots and in-product assistants', "Assistants that work inside your product's context and permissions, rather than a chat box on the side."),
            ('Retrieval over your knowledge', 'Search and answers grounded in your documents, tickets and databases, with sources the user can check.'),
            ('Document and data extraction', 'Structured data from contracts, invoices, forms and emails, with confidence scores and review queues.'),
            ('Evals and quality gates', 'Task-specific test sets, automated graders and regression checks that run on every change to prompts, models or code.'),
            ('LLMOps and cost control', 'Model routing, caching, observability and per-task cost tracking, so quality and spend stay visible.'),
        ],
        'phases': [
            ('Discovery', '1 to 2 weeks', 'We map the workflow, the data it needs and how success will be measured. You get a scored list of use cases and a build plan.'),
            ('Prototype on real data', '2 to 3 weeks', 'A working slice on your own data with a first eval set. This is where we learn what the model can and cannot do for you.'),
            ('Production build', '4 to 10 weeks', 'Integration with your systems, permissions, guardrails, monitoring and the full eval suite, released behind flags to real users.'),
            ('Run and improve', 'Ongoing', 'We track quality, latency and cost in production and improve against the eval set, or hand over to your team with runbooks.'),
        ],
        'ai_title': 'How AI changes the way we build it',
        'ai': [
            ('Evals written before features', 'We define what good looks like as test cases before writing the feature, so progress is measured rather than demoed.'),
            ('Model-agnostic architecture', 'Models sit behind an interface, so you can switch providers or bring a model in-house without a rewrite.'),
            ('Agents in our own pipeline', 'Our engineers use coding agents for scaffolding, tests and documentation, which leaves more of their time for design and review.'),
            ('Human review built in', 'Low-confidence results route to people with the context they need, and their decisions become new eval cases.'),
        ],
        'outcomes_title': 'What you own at the end',
        'outcomes': [
            'Production code in your repositories',
            'An eval suite with baseline scores',
            'Dashboards for quality, latency and cost',
            'Architecture decision records and runbooks',
            'A ranked backlog of next improvements',
        ],
        'models': ['sprint', 'pilot', 'pod'],
        'faqs': [
            ('Which models do you work with?', 'We work with the major frontier model providers and with open-weight models, and choose per task based on quality, latency, cost and where your data is allowed to go. The architecture keeps that choice reversible.'),
            ('Can it run inside our own cloud?', 'Yes. We deploy into your AWS, Azure or GCP accounts and can use private model endpoints or self-hosted open-weight models where data residency requires it.'),
            ('How do you stop the model making things up?', 'Grounding in your own data, constrained outputs, citations the user can check, confidence thresholds and human review for the cases that matter. The eval suite measures how often each of these holds.'),
            ('What if the prototype shows it will not work?', 'Then you find out in weeks rather than after a full build. Discovery and prototype are priced separately, so you can stop there with a clear answer.'),
        ],
        'related': ['legacy-modernization', 'forward-deployed-engineering'],
    },
    'forward-deployed-engineering': {
        'name': 'Forward-Deployed Engineering',
        'nav': 'Senior engineers embedded in your business, accountable for an outcome.',
        'short': 'Senior engineers embedded in your business who own a problem end to end, from the first conversation with users to the system running in production.',
        'start': 'Pods start within a few weeks, contracted monthly',
        'formation': 'pods',
        'title': "Engineers who stay with the problem until it's solved.",
        'lead': 'Forward-deployed engineers work inside your organization, close to the people who feel the problem. They scope it with your operators, build the software, integrate it with your systems and stay until it runs in production. This is how AI pilots stop being pilots.',
        'deliver_title': 'What a pod takes on',
        'deliver': [
            ('Problem framing with operators', 'Time with the teams who do the work, turning their pain points into a specific, measurable build.'),
            ('End-to-end delivery', 'One small team covers data, backend, AI, interface and deployment, so nothing waits on a handoff.'),
            ('Integration with what you already run', 'ERPs, CRMs, core banking, warehouse systems and the spreadsheets that hold them together.'),
            ('AI pilots taken to production', 'Existing proofs of concept hardened with security, monitoring, evals and support processes.'),
            ('Customer-facing deployments', "For product companies: engineers who deploy your platform into your customers' environments and feed what they learn back to product."),
            ('Capability transfer', 'Your people pair with ours throughout, so the knowledge stays when the pod moves on.'),
        ],
        'phases': [
            ('Embed', 'Week 1', 'The pod joins your teams, gets access, and spends time with the people who own the problem.'),
            ('Frame', 'Weeks 1 to 2', 'A written problem statement, success measures and a delivery plan you sign off.'),
            ('Build and deploy', 'Weeks 3 to 12', 'Weekly releases into your environment, with a working demo for stakeholders every week.'),
            ('Hand over or extend', 'End of term', 'Runbooks, recorded walkthroughs and paired handover, or the pod moves to the next problem.'),
        ],
        'ai_title': 'Where AI changes the work',
        'ai': [
            ('Faster first versions', 'Agents scaffold integrations and interfaces quickly, so operators react to working software in days instead of mockups.'),
            ('Reading unfamiliar systems', 'We use AI to map undocumented codebases, APIs and data models in your estate before we change anything.'),
            ('Operators in the loop', 'AI features ship with review steps your operators control, so trust builds with use.'),
            ('Measured in production', 'Every deployment tracks the business metric it was built to move, not only uptime.'),
        ],
        'outcomes_title': 'What you own at the end',
        'outcomes': [
            'A system in production, used by the people it was built for',
            'Measured movement on the agreed business metric',
            'Integration code and infrastructure in your accounts',
            'Runbooks, decision records and recorded walkthroughs',
            'Your engineers able to run and extend it',
        ],
        'models': ['pod', 'pilot'],
        'faqs': [
            ('How is this different from staff augmentation?', 'Staff augmentation adds engineers to your plan, managed by your leads. A forward-deployed pod owns an outcome: we frame the problem, decide how to solve it with you, and are accountable for the result.'),
            ('What does a pod look like?', 'Usually two to four engineers, led by a senior engineer who is your single point of accountability, with an architect available as the work needs.'),
            ('Do engineers need to be on site?', 'Some of the most valuable time is on site, especially in the first weeks. After that most pods work remotely with regular on-site days, depending on the problem and your location.'),
            ('How long is a typical engagement?', 'Most run three to six months per problem. Pods are contracted monthly, so you can extend, change scope or wind down with notice.'),
        ],
        'related': ['ai-first-engineering', 'staff-augmentation'],
    },
    'legacy-modernization': {
        'name': 'AI Modernization of Legacy Workflows',
        'nav': 'Digitize manual processes and replace legacy systems step by step.',
        'short': 'Digitize paper, email and spreadsheet processes and modernize the legacy systems behind them, using AI to read old code, recover business rules and automate the work.',
        'start': 'Usually starts with a 2 to 3 week assessment',
        'formation': 'layers',
        'title': 'Modernize the work, not just the code.',
        'lead': "Legacy is not only old code. It is the claims form that gets re-keyed, the approval chain that lives in email, the spreadsheet that runs month-end. We use AI to understand what these systems and processes actually do, then rebuild them step by step without stopping the business.",
        'deliver_title': 'What we modernize',
        'deliver': [
            ('Process digitization', 'Paper, PDF and email-driven processes turned into structured digital workflows with audit trails.'),
            ('Intelligent document processing', 'Extraction and validation for invoices, KYC files, claims, contracts and forms, with people reviewing the exceptions.'),
            ('Legacy code comprehension', 'AI-assisted mapping of large codebases: dependencies, data flows and the business rules buried in them, written down for people.'),
            ('Incremental replacement', 'Strangler-pattern migration: new services take over one capability at a time while the old system keeps running.'),
            ('Characterization testing', 'Tests generated from current behaviour, so the new system provably does what the old one did where it should.'),
            ('Data migration and reconciliation', 'Data moved out of legacy stores with automated reconciliation, so nothing is lost or counted twice.'),
        ],
        'phases': [
            ('Assess', '2 to 3 weeks', 'We map the process and the systems behind it with AI-assisted code and document analysis. You get a modernization map ranked by value and risk.'),
            ('Prove', '4 to 6 weeks', 'One slice modernized end to end, running alongside the old process so results can be compared.'),
            ('Scale', '3 to 9 months', 'Capability-by-capability migration with characterization tests and reconciliation at every step.'),
            ('Retire', 'As each slice lands', 'Old components are switched off once the new ones have matched them in production.'),
        ],
        'ai_title': 'Where AI changes the work',
        'ai': [
            ('Reading what nobody documented', 'Models summarize modules, trace data through old code and draft the business rules for your experts to confirm.'),
            ('Turning documents into data', 'Extraction models handle varied layouts and handwriting, with confidence scores that decide what a person checks.'),
            ("Tests from today's behaviour", 'AI generates characterization tests from production samples and logs, which makes refactoring safe.'),
            ('Faster, safer rewrites', 'Agents translate and refactor code under engineer review, while the test suite holds behaviour fixed.'),
        ],
        'outcomes_title': 'What you own at the end',
        'outcomes': [
            'A documented map of your current process and systems',
            'Business rules written down and confirmed by your experts',
            'Modernized workflows running in production',
            'Characterization and regression test suites',
            'A retirement plan for the remaining legacy components',
        ],
        'models': ['sprint', 'pilot', 'pod'],
        'faqs': [
            ('Do we have to stop using the old system?', 'No. We replace it one capability at a time, and old and new run side by side until the new one has proven itself.'),
            ('Our system is COBOL, VB6 or an old Java stack. Is that a problem?', 'No. AI-assisted comprehension works across older languages, and our engineers verify what it finds. The target stack is chosen with you.'),
            ('Can you work with scanned and handwritten documents?', 'Yes. Extraction quality varies by document type, so we measure it on a sample of your real documents during the assessment before committing to a target.'),
            ('How do you handle regulated data?', "Processing runs in your environment or approved regions, with access controls, audit logs and data handling agreed up front. We sign data processing agreements and work within GDPR and India's DPDP Act."),
        ],
        'related': ['platform-engineering', 'ai-consulting'],
    },
    'platform-engineering': {
        'name': 'Platform & Data Engineering',
        'nav': 'Cloud-native, event-driven, payments and data platforms built for scale.',
        'short': 'Cloud-native platforms, event-driven systems, payments and data infrastructure that stay reliable at scale and are ready for AI workloads.',
        'start': 'Usually starts with a 1 to 2 week architecture review',
        'formation': 'pipeline',
        'title': 'Platforms that hold at scale.',
        'lead': 'AI is only as good as the systems underneath it. We design and build the backends, data platforms and infrastructure that high-volume businesses run on: multi-tenant SaaS, payments, event streaming and analytics, engineered for failure from the start.',
        'deliver_title': 'What we build',
        'deliver': [
            ('Cloud-native backends', 'Services on Kubernetes or managed platforms, designed for horizontal scale and graceful failure.'),
            ('Event-driven architecture', 'Kafka-based streaming, event sourcing and change data capture for systems that react in real time.'),
            ('Multi-tenant SaaS', 'Tenant isolation, per-tenant configuration, metering and billing built into the platform.'),
            ('Payments and monetisation', 'Ledgers, payment orchestration, subscriptions and reconciliation, with idempotency and audit trails throughout.'),
            ('AI-ready data platforms', 'Pipelines, warehouses and real-time analytics stores with the governance and lineage AI work depends on.'),
            ('DevOps and reliability', 'Infrastructure as code, CI/CD, observability and SLOs, with on-call runbooks your team can use.'),
        ],
        'phases': [
            ('Architecture review', '1 to 2 weeks', 'Load, failure modes, data flows and cost reviewed against where the business is going. You get a prioritized plan.'),
            ('Foundations', '3 to 6 weeks', 'The pieces everything else depends on: environments, pipelines, observability and the core services.'),
            ('Build out', '2 to 6 months', 'Features and migrations delivered in increments, each with load tests and a rollback path.'),
            ('Operate', 'Ongoing', 'We hand over with runbooks and SLOs, or keep running and improving the platform with your team.'),
        ],
        'ai_title': 'Where AI changes the work',
        'ai': [
            ('Architecture analysis at speed', 'AI-assisted review of code, configuration and traces surfaces bottlenecks and risky dependencies early.'),
            ('Generated infrastructure, reviewed', 'Agents draft Terraform, pipelines and test harnesses; engineers review every change before it applies.'),
            ('Smarter operations', 'Anomaly detection and AI-assisted incident triage point on-call engineers at likely causes.'),
            ('Data built for models', 'Lineage, quality checks and access controls that let you put data in front of AI safely.'),
        ],
        'outcomes_title': 'What you own at the end',
        'outcomes': [
            'Architecture documented with decision records',
            'Infrastructure as code in your repositories',
            'Dashboards, alerts and SLOs',
            'Load and failure test results',
            'Runbooks and on-call guides',
        ],
        'models': ['sprint', 'pod', 'extension'],
        'faqs': [
            ('Which clouds and stacks do you work with?', 'AWS, Azure and GCP; Java and Spring Boot, Node.js, Go and Python; Kafka, PostgreSQL, ClickHouse, Redis and the major warehouses. We work in your stack before proposing a new one.'),
            ('Can you take over an existing platform?', 'Yes. We start with a review and a short shadowing period, then take on changes and operations in stages.'),
            ('Do you do cost optimization?', 'Yes. Architecture reviews usually find savings in compute, storage and data transfer, and we size them before recommending changes.'),
            ('Can you work alongside our platform team?', 'That is the usual setup. We agree ownership by service or capability so responsibilities stay clear.'),
        ],
        'related': ['legacy-modernization', 'staff-augmentation'],
    },
    'ai-consulting': {
        'name': 'AI Strategy & Deployed Consulting',
        'nav': 'Consultants inside your organization, from AI roadmap to first builds.',
        'short': 'Consultants who work inside your organization to decide where AI pays off, put the governance in place to use it safely, and stay through delivery.',
        'start': 'Usually starts with a 4-week assessment',
        'formation': 'bridge',
        'title': 'Advice that stays for the build.',
        'lead': 'The hard part of AI strategy is deciding which bets are worth making, lining up the data, security and legal answers, and seeing the first ones through. Our consultants are engineers, and they work inside your teams until the decisions turn into running systems.',
        'deliver_title': 'What we deliver',
        'deliver': [
            ('AI readiness assessment', 'Your data, systems, skills and policies reviewed against the use cases you care about, with the gaps sized.'),
            ('Use-case portfolio', 'Opportunities scored by value, feasibility and risk, so you fund the few that matter.'),
            ('Architecture and build-versus-buy', 'Reference architectures and vendor evaluations based on your constraints rather than a partner list.'),
            ('AI governance and policy', "Usage policies, model risk controls and review processes aligned with the EU AI Act, GDPR and India's DPDP Act."),
            ('Engineering practice uplift', 'AI coding tools, evals and agent workflows brought into your own engineering teams, with measurement.'),
            ('Fractional technical leadership', 'Experienced engineering leaders, part-time, to steer AI and platform decisions.'),
        ],
        'phases': [
            ('Listen', 'Week 1', 'Interviews with leadership, operators and engineers, plus a review of systems and data.'),
            ('Assess', 'Weeks 2 to 3', 'Readiness findings and a scored use-case portfolio, presented as decisions to make.'),
            ('Plan', 'Week 4', 'A 90-day roadmap with owners, budgets, governance steps and the first builds specified.'),
            ('Deploy', 'Ongoing', 'Consultants stay embedded to run the first builds with your teams or ours, and adjust the plan as results come in.'),
        ],
        'ai_title': 'How we keep it practical',
        'ai': [
            ('Evidence over opinion', 'Short technical spikes on your own data test whether a use case works before it goes on the roadmap.'),
            ('Your engineering, measured', 'We baseline delivery metrics before introducing AI tooling, so you can see what changed.'),
            ('Governance that ships', 'Policies come with the checks that enforce them: approved models, logging and review gates.'),
            ('Practitioners, not presenters', 'Every consultant can build what they recommend, which keeps recommendations realistic.'),
        ],
        'outcomes_title': 'What you own at the end',
        'outcomes': [
            'A scored AI use-case portfolio',
            'A 90-day roadmap with owners and budgets',
            'An AI usage policy and governance process',
            'Reference architecture and vendor recommendations',
            'Baseline delivery metrics for your engineering teams',
        ],
        'models': ['sprint', 'advisory'],
        'faqs': [
            ('Is this a one-off assessment?', 'It can be. Many clients keep a consultant embedded part-time after the assessment to steer delivery and adjust the plan.'),
            ('Do you resell AI platforms?', 'No. We have no reseller arrangements, so recommendations follow your requirements.'),
            ('Who will we work with?', 'Senior engineers and architects with delivery experience, supported by specialists in data, security and compliance as needed.'),
            ('Can you help with regulation such as the EU AI Act?', 'We help you classify use cases, design the technical controls and document them. Legal sign-off stays with your counsel.'),
        ],
        'related': ['ai-first-engineering', 'forward-deployed-engineering'],
    },
    'staff-augmentation': {
        'name': 'Staff Augmentation',
        'nav': 'Vetted senior engineers who join your team and work to your plan.',
        'short': 'Senior engineers who join your team, your tools and your rituals, with the AI-assisted habits that make them productive from the first sprint.',
        'start': 'Shortlist within a week of the brief',
        'formation': 'grid',
        'title': 'Senior engineers, added to your team.',
        'lead': 'When your roadmap is clear and you need more senior hands, our engineers join your team directly. They work in your repositories, attend your standups and report to your leads, backed by Otorithm for vetting, onboarding, replacement and ongoing quality checks.',
        'deliver_title': 'Roles we place',
        'deliver': [
            ('Backend engineers', 'Java and Spring Boot, Node.js, Go and Python engineers for APIs, services and integrations.'),
            ('Frontend and mobile engineers', 'React, Next.js, React Native and Flutter engineers who care about performance and accessibility.'),
            ('AI and ML engineers', 'Specialists in LLM applications, retrieval, agents, evals and MLOps.'),
            ('Data engineers', 'Pipelines, streaming, warehouses and analytics engineering.'),
            ('Platform and DevOps engineers', 'Cloud infrastructure, Kubernetes, CI/CD and observability.'),
            ('Engineering and delivery leads', 'Tech leads and engagement managers who can run a team within yours.'),
        ],
        'phases': [
            ('Brief', 'Day 1', 'A call to agree role, stack, seniority, time-zone overlap and how the engineer will work with your team.'),
            ('Shortlist', 'Within a week', 'Profiles of vetted engineers who match the brief, with notes from our technical interviews.'),
            ('Interview', 'Your process', 'You interview and choose. We arrange scheduling around your team.'),
            ('Onboard and review', 'Ongoing', 'A structured onboarding, then a monthly check-in with you from our engagement lead.'),
        ],
        'ai_title': 'What you get beyond a CV',
        'ai': [
            ('AI-fluent by default', 'Our engineers are trained to work with coding agents and AI tools, within the policies you set.'),
            ('Vetted on real work', 'Every engineer passes a hands-on coding exercise, a system design round and a communication assessment.'),
            ('Backed by a practice', 'Engineers can draw on our practice leads for architecture questions and code review.'),
            ('Covered if the fit is wrong', 'If an engineer is not the right fit, we propose a replacement and cover the handover.'),
        ],
        'outcomes_title': 'Terms in brief',
        'outcomes': [
            'Monthly billing per engineer, without long lock-ins',
            'All IP assigned to you in the contract',
            'Confidentiality and non-solicitation terms',
            'Working-hour overlap agreed per role',
            'A named engagement lead for escalation',
        ],
        'models': ['extension', 'pod'],
        'faqs': [
            ('How quickly can someone start?', 'Typically two to four weeks from the brief, depending on seniority and your interview process.'),
            ('Can we hire an engineer permanently?', 'Yes, after an agreed minimum period, with a conversion fee set in the contract.'),
            ('What time zones do your engineers cover?', 'Our engineers work from India. They overlap most of the working day with Europe and keep agreed overlap hours with North America, typically three to four hours.'),
            ('Do engineers use AI tools on our code?', 'Only the tools your policies allow. We agree an AI usage policy for each engagement before work starts.'),
        ],
        'related': ['forward-deployed-engineering', 'platform-engineering'],
    },
}

CHOOSER = [
    ('You have an AI idea and need it working in production.', 'ai-first-engineering'),
    ('A business process still runs on paper, email or a system nobody wants to touch.', 'legacy-modernization'),
    ('You need a team to own an outcome inside your business.', 'forward-deployed-engineering'),
    ('Your roadmap is clear and you need more senior hands.', 'staff-augmentation'),
    ('You need to decide where AI fits before you build anything.', 'ai-consulting'),
    ("Your platform won't scale to what the business needs next.", 'platform-engineering'),
]

# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------
HOME = {
    'label': 'AI-native engineering consultancy',
    'title': 'Engineering, rebuilt around AI.',
    'lead': 'Otorithm designs, builds and modernizes production software for product companies and enterprises. Senior engineers lead every engagement, and AI runs through every step of how we deliver, from reading your legacy code to testing what we ship.',
    'agent_intro': ('Hey there, meet O.T.T.O,', "Otorithm's Talent & Tech Orchestrator"),
    'typed': "Glad you're here. Senior engineers, AI in every step of delivery, zero hiring drag. So, what are we building?",
    'pills': [
        ('Build an AI product', 'services/ai-first-engineering.html'),
        ('Modernize a legacy workflow', 'services/legacy-modernization.html'),
        ('Embed an engineering pod', 'services/forward-deployed-engineering.html'),
        ('Add senior engineers', 'services/staff-augmentation.html'),
    ],
    'diff_label': 'How we are different',
    'diff_title': 'AI is in how we work, not only in what we build.',
    'diff_body': 'Most firms add AI to the product and keep delivering the old way. We rebuilt our delivery around it. Agents draft, test and document under the direction of senior engineers, and every output passes the same review gates as hand-written work. You get the speed of AI with an engineer accountable for every change.',
    'why': [
        ('Senior engineers only', 'Every engineer we deploy has shipped and run production systems. Nobody learns the basics on your time.'),
        ('Payments-grade engineering', 'Our engineers have built and run payments and monetisation platforms at global marketplace scale, so we design for audit trails, idempotency and failure from day one.'),
        ('Your code, your cloud', 'Work lands in your repositories and runs in your accounts. Models run in your tenancy or through enterprise APIs with zero data retention.'),
        ('Time zones that work', 'Our delivery centre in Gurugram overlaps most of the working day with Europe and keeps dedicated overlap hours with North America.'),
    ],
}

# The delivery loop (shared by Home and Approach)
LOOP = [
    ('Frame', 'We turn your goals, systems and constraints into context packs: architecture notes, domain glossaries and acceptance criteria that engineers and agents both work from.'),
    ('Generate', 'Agents produce first drafts of code, tests, migrations and documentation. Engineers direct the work and make the design calls.'),
    ('Verify', "Automated tests, eval suites, security scans and human review gate every change. Nothing merges on a model's say-so."),
    ('Ship', 'Small, reversible releases through CI/CD and feature flags, into your cloud and your repositories.'),
    ('Observe', 'Production telemetry, eval drift and cost per task feed straight back into the next cycle.'),
]

# ---------------------------------------------------------------------------
# Industries
# ---------------------------------------------------------------------------
INDUSTRIES = [
    {
        'id': 'fintech',
        'name': 'Fintech & payments',
        'intro': 'Payment flows, lending and wealth platforms where correctness, latency and audit trails come first.',
        'build': ['Payment orchestration and ledgers', 'Lending and onboarding journeys', 'Reconciliation and settlement', 'Fraud and risk tooling'],
        'ai': ['KYC document extraction and checks', 'Transaction categorization and anomaly detection', 'Agent-assisted dispute and chargeback handling', 'Collections and support copilots'],
    },
    {
        'id': 'financial-services',
        'name': 'Banking & financial services',
        'intro': 'Banks, insurers and NBFCs modernizing core processes under close regulatory scrutiny.',
        'build': ['Digital onboarding and servicing', 'Integration layers around core systems', 'Regulatory reporting pipelines', 'Advisor and relationship tools'],
        'ai': ['Claims and application intake automation', 'Policy and procedure search for staff', 'Credit memo and report drafting with review', 'Model governance aligned with the EU AI Act'],
    },
    {
        'id': 'marketplaces',
        'name': 'Marketplaces & e-commerce',
        'intro': 'Two-sided platforms and retailers that live on listing quality, search and conversion.',
        'build': ['Monetisation and listing products', 'Search and recommendation services', 'Seller and buyer tooling', 'Checkout and payouts'],
        'ai': ['Listing quality and moderation', 'Semantic search and ranking', 'Seller support copilots', 'Catalogue enrichment from images and text'],
    },
    {
        'id': 'saas',
        'name': 'B2B SaaS',
        'intro': 'Software companies adding AI to their products and scaling platforms for larger customers.',
        'build': ['Multi-tenant platform architecture', 'Usage metering and billing', 'Enterprise features: SSO, audit and RBAC', 'Integrations and public APIs'],
        'ai': ['In-product copilots and agents', 'Retrieval over customer data that respects permissions', 'AI feature evals and cost controls', 'Customer deployments by forward-deployed engineers'],
    },
    {
        'id': 'logistics',
        'name': 'Logistics & supply chain',
        'intro': 'Operators where shipments, documents and exceptions move faster than the systems built to track them.',
        'build': ['Shipment and order tracking platforms', 'Partner and carrier integrations', 'Warehouse and fleet operations tools', 'Real-time operational dashboards'],
        'ai': ['Bills of lading, invoices and customs documents turned into data', 'Exception triage and routing', 'ETA and demand forecasting', 'Assistants for dispatch and operations teams'],
    },
    {
        'id': 'healthcare',
        'name': 'Healthcare operations',
        'intro': 'Providers and health platforms reducing administrative load while keeping patient data protected.',
        'build': ['Patient and provider portals', 'Scheduling and referral workflows', 'Interoperability with health record systems', 'Claims and billing tooling'],
        'ai': ['Referral and intake document processing', 'Prior authorization support with human review', 'Documentation summaries for administrative staff', 'Operational forecasting'],
    },
]

# ---------------------------------------------------------------------------
# Approach
# ---------------------------------------------------------------------------
PRINCIPLES = [
    ('Engineers stay accountable', 'Every change has a named engineer who reviewed it and owns it. AI speeds up the work; it never signs it off.'),
    ('Evals before demos', 'For AI features we agree the test set and the pass mark before we build, and report against it every week.'),
    ('Context is a deliverable', 'Architecture notes, domain glossaries and decision records are kept current. They make people and agents productive, and they stay with you.'),
    ('Your code, your cloud, your keys', 'Repositories, infrastructure and model accounts belong to you from day one. We work with access you grant and can revoke.'),
    ('Measure the work', 'We report delivery metrics such as lead time and change failure rate and, for AI features, quality and cost per task.'),
]

LIFECYCLE = [
    ('Discover', 'A call, then a short scoping exercise. We meet the people who own the problem and look at the systems involved.', 'A written problem statement and a proposal with options.'),
    ('Shape', 'We agree success measures, the team, the engagement model and the AI usage policy for the work.', 'A signed scope, a delivery plan and access set up.'),
    ('Build', 'Weekly releases, a weekly demo and a written status note. Risks and decisions are logged as they come up.', 'Working software in your environment, every week.'),
    ('Transfer or scale', 'Paired handover to your team, or the engagement grows to the next problem with the same people.', 'Runbooks, decision records and a team that can run it.'),
]

SECURITY = [
    ('Confidentiality', 'NDAs and IP assignment in every contract, for Otorithm and for each engineer on the engagement.'),
    ('Access', 'Least-privilege access to your systems, managed through your identity provider where possible and removed at roll-off.'),
    ('AI usage', 'An agreed AI usage policy per engagement: which tools and models, which data they may see and how outputs are reviewed. Enterprise APIs with zero data retention by default.'),
    ('Data protection', "Data processing agreements, and EU Standard Contractual Clauses where needed. Processing aligned with GDPR and India's DPDP Act."),
    ('Secure delivery', 'Secrets in vaults, dependency and container scanning in CI, and encrypted, managed devices for everyone on the engagement.'),
]

TIMEZONES = [
    ('India', 'IST', 'Full working day'),
    ('Middle East', 'GST', 'Full working day'),
    ('Europe and UK', 'CET / GMT', 'Most of the working day, with engineers on an 11:30 to 20:30 IST schedule'),
    ('North America', 'ET / PT', 'Three to four hours with the East Coast; schedules agreed per team for the West Coast'),
]

# ---------------------------------------------------------------------------
# Work: engagement blueprints (patterns, not client stories)
# ---------------------------------------------------------------------------
BLUEPRINTS = [
    {
        'id': 'pilot-to-production',
        'title': 'Taking an AI pilot to production in one quarter',
        'services': ['forward-deployed-engineering', 'ai-first-engineering'],
        'fits': 'A promising proof of concept has stalled. It works in a demo, but nobody trusts it with real customers or real money.',
        'steps': [
            ('Weeks 1–2', 'Audit the pilot and build an eval set from real cases, including the awkward ones.'),
            ('Weeks 3–6', 'Harden it: grounding, guardrails, permissions, monitoring and cost limits.'),
            ('Weeks 7–10', 'Staged rollout behind feature flags, with a review queue for low-confidence results.'),
            ('Weeks 11–12', 'Handover with runbooks, dashboards and a ranked improvement backlog.'),
        ],
        'end': ['A production system with real users', 'Eval scores tracked week by week', 'Quality, latency and cost dashboards', 'Runbooks your team can operate'],
    },
    {
        'id': 'digitize-onboarding',
        'title': 'Digitizing a paper-heavy onboarding flow',
        'services': ['legacy-modernization'],
        'fits': 'Applications arrive as scans and email attachments, and an operations team re-keys them into a core system.',
        'steps': [
            ('Weeks 1–3', 'Sample real documents and measure extraction accuracy field by field before committing to targets.'),
            ('Weeks 4–8', 'Extraction, validation and a review queue, run in parallel with the manual process for comparison.'),
            ('Weeks 9–14', 'Integration with the core system, rolled out one document type at a time.'),
            ('After launch', 'Accuracy monitored per field, and reviewer corrections fed back into the evals.'),
        ],
        'end': ['Structured intake with an audit trail', 'A review queue for exceptions only', 'Accuracy reports per document type', 'Fewer manual touches per application'],
    },
    {
        'id': 'replace-legacy-module',
        'title': 'Mapping and replacing a legacy core module',
        'services': ['legacy-modernization', 'platform-engineering'],
        'fits': 'A critical system is old, thinly documented and blocks every new feature that touches it.',
        'steps': [
            ('Weeks 1–3', 'AI-assisted code mapping and a business rules catalogue, confirmed by your experts.'),
            ('Weeks 4–8', 'Characterization tests from production behaviour, and the first capability moved behind a facade.'),
            ('Month 3 onward', 'Capability-by-capability migration with automated reconciliation.'),
            ('Each release', 'Old components retired once the new ones have matched them in production.'),
        ],
        'end': ['Documented business rules', 'Characterization test suites', 'New services in your cloud', 'A retirement plan for what remains'],
    },
    {
        'id': 'saas-enterprise-ready',
        'title': 'Making a SaaS platform enterprise-ready',
        'services': ['platform-engineering'],
        'fits': 'Larger customers want SSO, audit logs, data isolation and uptime commitments the platform was not built for.',
        'steps': [
            ('Weeks 1–2', 'Architecture review and load tests against the enterprise requirements.'),
            ('Weeks 3–8', 'Tenant isolation, SSO and role-based access, and audit logging.'),
            ('Weeks 9–16', 'Usage metering, SLOs with alerting, and disaster recovery drills.'),
            ('Ongoing', 'Platform team support while your engineers take ownership.'),
        ],
        'end': ['Enterprise features customers ask for', 'Documented SLOs and alerting', 'Tested recovery procedures', 'Architecture decision records'],
    },
    {
        'id': 'product-copilot',
        'title': 'Adding an AI copilot to a B2B product',
        'services': ['ai-first-engineering'],
        'fits': 'Customers are asking for AI features, competitors are shipping them, and the team needs to move without breaking trust.',
        'steps': [
            ('Weeks 1–2', 'Find the tasks users repeat most and define what a correct answer looks like for each.'),
            ('Weeks 3–6', "Retrieval over customer data that respects each user's permissions, and a first eval suite."),
            ('Weeks 7–10', 'Beta with design-partner customers, with feedback captured as new eval cases.'),
            ('Launch', 'General release with cost controls, usage analytics and quality monitoring.'),
        ],
        'end': ['A copilot inside your product', 'Evals that run on every change', 'Cost per conversation tracked', 'A roadmap built from real usage'],
    },
    {
        'id': 'roadmap-push',
        'title': 'Extending a team for a roadmap push',
        'services': ['staff-augmentation'],
        'fits': 'The roadmap is set, hiring is slow and a launch date is fixed.',
        'steps': [
            ('Week 1', 'Brief, then a shortlist of vetted engineers matched to your stack and time zone.'),
            ('Weeks 2–3', 'Your interviews, then contracts and access.'),
            ('Weeks 3–4', 'Structured onboarding into your repositories, rituals and tooling.'),
            ('Monthly', 'Engagement lead check-ins, with scale up or down on notice.'),
        ],
        'end': ['Roadmap capacity when you need it', 'Engineers working inside your process', 'Documented, reviewed code', 'An option to hire engineers permanently'],
    },
]

# ---------------------------------------------------------------------------
# About
# ---------------------------------------------------------------------------
ABOUT = {
    'title': 'An engineering firm built around AI.',
    'lead': 'Otorithm is a software engineering consultancy for product companies and enterprises in India, Europe and North America. We build, modernize and run production systems with senior engineers, and we use AI throughout our own delivery.',
    'beliefs': [
        ('Seniority is the strategy', 'AI makes good engineers faster and weak processes riskier. We staff every engagement with people who have run production systems.'),
        ('AI raises the bar for engineering', 'When drafting code gets cheap, judgement, testing and review matter more. That is where our engineers spend their time.'),
        ('Outcomes over output', 'We agree what success means before we start, then report against it. Hours and story points are not the goal.'),
        ('Leave clients stronger', 'Documentation, decision records and paired work mean your team can run what we build without us.'),
    ],
    'practices': [
        ('AI Engineering', 'Agents, copilots, retrieval, document AI, evals and LLMOps.'),
        ('Platform & Data', 'Cloud-native backends, event streaming, payments, data platforms and reliability.'),
        ('Product Engineering', 'Web and mobile applications, design systems and product delivery.'),
        ('Modernization', 'Legacy comprehension, process digitization and incremental migration.'),
    ],
    'responsible': [
        'We tell clients where and how AI is used in their delivery.',
        'A named engineer reviews and owns every change, whoever drafted it.',
        'Client data is never used to train models, ours or anyone else\'s.',
        'We send models the minimum data a task needs, in approved regions.',
        'User-facing AI features are tested for failure modes, bias and misuse before release.',
    ],
}

# ---------------------------------------------------------------------------
# Careers
# ---------------------------------------------------------------------------
CAREERS = {
    'title': 'Build serious software, with AI at your side.',
    'lead': 'We hire senior engineers who like hard problems, care about craft and want to use the best AI tools on real production systems for clients around the world.',
    'why': [
        ('Real production work', 'Payments, platforms, data and AI systems that businesses depend on, not throwaway prototypes.'),
        ('AI tools, properly', 'Coding agents and AI tooling are part of how we work, with the practices that make them safe to use.'),
        ('Seniors around you', 'Practice leads who review your design decisions and pair on the difficult parts.'),
        ('Global clients from India', 'Work with teams in Europe and North America from our Gurugram delivery centre or remotely.'),
    ],
    'process': [
        ('Apply', 'Send your profile and a note on the work you are proudest of.'),
        ('Intro call', 'Thirty minutes about your experience and what you want next.'),
        ('Practical exercise', 'A realistic coding task, done with the tools you normally use, AI included, followed by a walkthrough.'),
        ('System design', 'A conversation about how you would build and run a system like the ones our clients rely on.'),
        ('Offer', 'Meet the people you would work with, then an offer.'),
    ],
    'roles': [
        ('Senior Backend Engineer', 'Java and Spring Boot, event-driven systems', 'Platform & Data', 'Gurugram, hybrid'),
        ('Senior AI Engineer', 'LLM applications, retrieval, agents and evals', 'AI Engineering', 'India, remote'),
        ('Forward-Deployed Engineer', 'Full-stack delivery inside client teams', 'AI Engineering', 'Gurugram, hybrid'),
        ('Senior Data Engineer', 'Streaming, pipelines and warehouses', 'Platform & Data', 'India, remote'),
        ('Senior Frontend Engineer', 'React, Next.js and design systems', 'Product Engineering', 'India, remote'),
        ('Platform Engineer', 'Kubernetes, Terraform, CI/CD and observability', 'Platform & Data', 'Gurugram, hybrid'),
    ],
}

# ---------------------------------------------------------------------------
# Insights (original articles)
# ---------------------------------------------------------------------------
ARTICLES = [
    {
        'slug': 'forward-deployed-engineering-vs-staff-augmentation',
        'title': 'Forward-deployed engineering or staff augmentation? How to choose',
        'summary': 'Both put outside engineers in your team. The difference is who owns the outcome, and that decides which one you need.',
        'topic': 'Engagement models',
        'minutes': 6,
        'services': ['forward-deployed-engineering', 'staff-augmentation'],
        'html': '''
<p>Both models put outside engineers inside your organization, and from a distance they look the same: people in your standups, commits in your repositories, a monthly invoice. The difference is ownership. With staff augmentation, you own the plan and the outcome. With forward-deployed engineering, the team you bring in owns a problem and is accountable for solving it.</p>
<p>Choosing the wrong one is expensive in both directions. Augmented engineers on an unframed problem wait for direction that never comes. A forward-deployed pod on a well-specified backlog is paying for framing work you have already done.</p>

<h2>Staff augmentation adds capacity to your plan</h2>
<p>Staff augmentation works when you already know what to build. Your architecture is settled, your product and engineering leads set priorities, and the constraint is hands on keyboards. The engineers you bring in work like your own: your rituals, your code review, your definition of done.</p>
<p>It is the faster and cheaper option per engineer, and it scales well. Its limit is that it only amplifies the direction you give it. If the direction is unclear, more engineers make the confusion more expensive.</p>

<h2>Forward-deployed engineering owns a problem</h2>
<p>Forward-deployed engineering grew out of companies that deploy complex software into their customers' organizations. Engineers sit with the people who have the problem, decide what to build with them, build it and stay until it runs. The model fits work where the problem is clear but the solution is not.</p>
<p>It is the right choice when:</p>
<ul>
<li>the work crosses teams and systems no single internal team controls;</li>
<li>the people who understand the problem are operators, not engineers;</li>
<li>an AI pilot works in a demo but has never been trusted in production;</li>
<li>success is a business metric, not a list of delivered tickets.</li>
</ul>

<h2>Five questions that decide it</h2>
<ol>
<li><strong>Do you know exactly what needs building?</strong> If yes, augment. If you know the problem but not the solution, deploy.</li>
<li><strong>Who makes the day-to-day decisions?</strong> Augmented engineers need a lead on your side with time to direct them. A pod brings its own lead.</li>
<li><strong>Does the work cross boundaries?</strong> Operations, IT, security and compliance in one project favour a pod that can work across them.</li>
<li><strong>How will you measure success?</strong> Velocity and delivered scope suit augmentation. A moved business metric suits a pod.</li>
<li><strong>What happens when the engagement ends?</strong> Augmented engineers leave knowledge in your team as they go. A pod needs a planned handover, and you should ask for it in the contract.</li>
</ol>

<h2>How the costs compare</h2>
<p>Per engineer, rates are similar. A pod costs more per month because it includes a senior lead and time for framing, stakeholder work and integration that augmented engineers would not do. The fair comparison is cost per outcome. Augmentation looks cheaper until you count the management time your own leads spend directing it.</p>

<h2>Using both</h2>
<p>A common pattern is to start with a forward-deployed pod to frame the problem and ship the first version, then extend the team with augmented engineers to scale it, with the pod lead staying on as tech lead. You get clear ownership while the shape of the work is uncertain and cheaper capacity once it is not.</p>
''',
    },
    {
        'slug': 'modernizing-legacy-workflows-with-ai',
        'title': 'Modernizing legacy workflows with AI: start with the business rules',
        'summary': 'Most modernization programmes fail on knowledge, not technology. AI changes the economics of recovering what the old system knows.',
        'topic': 'Modernization',
        'minutes': 7,
        'services': ['legacy-modernization', 'platform-engineering'],
        'html': '''
<p>Legacy modernization rarely fails because the new technology is hard. It fails because the old system knows things nobody wrote down: the discount that only applies on the last business day of a quarter, the field that means something different for customers onboarded before a merger, the manual check an operator does because the system once got it wrong.</p>
<p>Those rules are requirements. A rewrite that misses them is a regression, however modern the stack. AI does not remove that problem, but it makes recovering the rules far cheaper than it used to be. That changes how a modernization programme should be run.</p>

<h2>Why big rewrites go wrong</h2>
<p>The classic approach is to specify the new system from interviews and documentation, build it, and switch over. The specification is incomplete because the knowledge is in the code and in people's habits, not in documents. The gaps surface after cutover, when they are most expensive to fix.</p>

<h2>Step 1: recover the rules</h2>
<p>Language models are good at reading code that nobody wants to read. We use them to summarize modules, trace how data moves through the system and draft a catalogue of the business rules they find. Your domain experts then confirm, correct or reject each rule.</p>
<p>The confirmed catalogue becomes the specification for the new system. It is also the first durable documentation the old system has had, which is useful whether or not you replace it.</p>
<blockquote>A hallucinated business rule is worse than a missing one, because it looks authoritative. Every rule the model drafts needs a person to confirm it.</blockquote>

<h2>Step 2: pin today's behaviour with tests</h2>
<p>Before changing anything, capture what the system does now. Characterization tests record current behaviour from production samples and logs, so any change in behaviour is visible. AI generates candidate tests quickly; engineers curate them and decide which behaviours are intended and which are bugs to fix on purpose.</p>

<h2>Step 3: digitize the inputs</h2>
<p>Many legacy workflows start on paper: scanned forms, emailed PDFs, faxed documents. Document extraction models can turn these into structured data, but accuracy varies by document type and by field. Measure it on a sample of your real documents before setting targets, and design a review queue so that low-confidence fields go to a person while the rest flow straight through.</p>

<h2>Step 4: replace one capability at a time</h2>
<p>Put a facade in front of the old system and move capabilities behind it one by one. Run old and new in parallel and reconcile their outputs automatically. Retire each legacy component once the new one has matched it in production for long enough to trust. The business keeps running throughout.</p>

<h2>Where AI does not help yet</h2>
<ul>
<li>Deciding what the business should do. When two rules contradict each other, a person has to choose.</li>
<li>Accountability for regulated decisions. The model can draft; a named person signs off.</li>
<li>Verifying its own output. Recovered rules and generated tests are hypotheses until checked.</li>
</ul>

<h2>What to measure</h2>
<p>Track the share of business rules confirmed by experts, test coverage of the critical paths, extraction accuracy per field, manual touches per case, and the number of legacy components retired. These tell you whether the programme is reducing risk, not just producing code.</p>
''',
    },
    {
        'slug': 'evals-before-demos',
        'title': 'Evals before demos: how we take AI features to production',
        'summary': 'A demo shows the best cases. Production sees all of them. An eval suite is how you know which one you have built.',
        'topic': 'AI engineering',
        'minutes': 6,
        'services': ['ai-first-engineering', 'ai-consulting'],
        'html': '''
<p>Most AI features are approved on the strength of a demo. Someone picks a handful of examples, the model handles them well, and the room agrees to build. Then production arrives with the long tail: ambiguous inputs, missing data, users who phrase things in ways nobody expected. Quality turns out to be a distribution, and the demo showed only its best end.</p>
<p>We work the other way round. Before building an AI feature, we agree how it will be tested and what score counts as good enough. The feature is done when it passes, not when it impresses.</p>

<h2>Start with the test set</h2>
<p>Collect real cases from the workflow the feature will serve: a few hundred is often enough to start. Include the awkward ones on purpose. For each case, write down what a correct result looks like. Then agree the pass mark with the people who own the outcome, before any code exists. This conversation often changes the scope, which is cheaper now than later.</p>

<h2>Grade automatically, check by hand</h2>
<p>Use deterministic checks wherever the output allows it: schema validity, exact fields, required citations. For open-ended text, use rubric-based grading by a model, calibrated against human ratings on a sample so you know how far to trust it. Keep a regular human review of a random sample, because graders drift too.</p>

<h2>Make every change earn its place</h2>
<p>Prompts, retrieval settings, model versions and code all change behaviour. Run the eval suite in CI on every change, and treat a regression the way you would treat a failing test: it blocks the merge until someone decides it is acceptable. This is what lets a team improve an AI feature quickly without fear.</p>

<h2>Watch production</h2>
<ul>
<li>Sample live traffic into a review queue and grade it with the same rubric.</li>
<li>Track quality, latency and cost per task side by side.</li>
<li>Turn every new failure into a new eval case, so it cannot quietly come back.</li>
</ul>

<h2>Decide with numbers</h2>
<p>Evals turn model choice into an engineering decision. If a smaller, cheaper model passes the easy cases at the same rate as a larger one, route those cases to it and keep the larger model for the hard ones. If a new model release scores better on your suite, switching is a measured decision rather than a hope.</p>
<p>A good eval suite outlives any single model. It encodes what your business means by a correct answer, and that is the asset worth building first.</p>
''',
    },
]
