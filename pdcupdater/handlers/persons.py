import pdcupdater.services
import pdcupdater.handlers


class NewPersonHandler(pdcupdater.handlers.BaseHandler):
    """ When a new person gets added to FAS. """

    def __init__(self, *args, **kwargs):
        super(NewPersonHandler, self).__init__(*args, **kwargs)
        self.fas_config = self.config['pdcupdater.fas']

    @property
    def topic_suffixes(self):
        return ['fas.user.create']

    def can_handle(self, pdc, msg):
        return msg['topic'].endswith('fas.user.create')

    def handle(self, pdc, msg):
        username = msg['msg']['user']
        email = f'{username}@fedoraproject.org'
        pdc['persons']._({'username': username, 'email': email})

    def audit(self, pdc):
        # Query the data sources
        fas_persons = pdcupdater.services.fas_persons(**self.fas_config)
        pdc_persons = pdc.get_paged(pdc['persons']._)

        # normalize the two lists
        fas_persons = {p['username'] for p in fas_persons}
        pdc_persons = {p['username'] for p in pdc_persons}

        # use set operators to determine the difference
        present = pdc_persons - fas_persons
        absent = fas_persons - pdc_persons

        return present, absent

    def initialize(self, pdc):
        fas_persons = pdcupdater.services.fas_persons(**self.fas_config)
        persons = [{
            'username': person['username'],
            'email': f"{person['username']}@fedoraproject.org",
        } for person in fas_persons]
        for person in persons:
            try:
                pdc['persons']._(person)
            except beanbag.bbexcept.BeanBagException as e:
                log.warn("persons, %r %r", component, e.response)
