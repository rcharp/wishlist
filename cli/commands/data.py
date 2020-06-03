def statuses():
    return [{'name': 'In backlog', 'color': 'blue'},
            {'name': 'Already exists', 'color': 'red'},
            {'name': 'In planning', 'color': 'orange'},
            {'name': 'In development', 'color': 'green'},
            {'name': 'Shipped', 'color': 'yellow'},
            {'name': 'In beta', 'color': 'purple'},
            {'name': 'Future', 'color': 'gray'}]


def titles():
    return ['Allow users to add their own comment sections',
            'Add a feedback feature to the website',
            'User login and membership functionality',
            'Better Asset Management',
            'Multi-language sites and CMS fields',
            'Sell Digital Goods',
            'Ability to style CSS Combinators: combo classes, pseudo classes, nested classes']


def descriptions():
    return ['All we are looking for is selling a digital good, and creating unique links to be sent via email for now. A full "my account" experience would be nice down the road. ',
                'Each page and CMS entry is translatable. When creating fields for a Collection, mark whether that field is translatable (some fields won\'t need translation, like references to other collections, price fields, etc). An option for Links should be added to choose a language (in addition to external links, pages within the site, etc).',
                'Easily sort and organize assets (drag/move - organize in folders)'
                'Take bulk actions ( multiple asset upload - multiple select - move to folders - delete assets)'
                'Rename assets and define image alt text'
                'Replace every instance of an asset throughout the project by replacing it in the Asset Manager'
                'Find assets in the manager using a search bar',
                'Allow users to sign up on your websites with a username & password. Enable/disable access to content/pages for different user types.',
                'When I add a css class and then add another css class on top of it, the resulting css rule in the code is a compound rule. Most of the time this is fine, but there are times I need the two rules to be separate. Please expand on the css layering, by giving us granular options for creating single-class or compound rules, and maybe even some complex bits like parent/sibling selectors, or ":" suffix rules.'
                'Mainly, if I\'ve got two elements, and one\'s got classes A->B->D while the other\'s got classes A->C->D, I don\'t want to have to define D twice, like I do now.']