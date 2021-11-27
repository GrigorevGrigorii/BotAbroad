class ActionsEnum:
    ADD = 'add'
    REMOVE = 'remove'
    SHOW = 'show'


ACTION_TO_DISPLAY_NAME = {
    ActionsEnum.ADD: 'Добавить страну в подписки',
    ActionsEnum.REMOVE: 'Убрать страну из подписок',
    ActionsEnum.SHOW: 'Посмотреть подписки'
}

DISPLAY_NAME_TO_ACTION = {
    ACTION_TO_DISPLAY_NAME[action]: action
    for action in ACTION_TO_DISPLAY_NAME.keys()
}
