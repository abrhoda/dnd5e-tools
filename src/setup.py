import logging
from pathlib import Path
import json
from utils import convert_to_float

from models import Monster, StatBlock, ActionsBlock, VariantBlock, LairActionsBlock, RegionalEffectsBlock, Item

logger = logging.getLogger(__name__)

class FileParser():
    def __init__(self, path: Path):
        self.path: Path = path

def setup(source: str, _type: str = 'ALL') -> None:
    target: Path = Path(source) 
    if not target.exists() or not target.is_dir():
        logger.error(f'Source does not point to 5e.tool local repo. See `python main.py setup --help` for more info.')
        return
    if _type == 'ALL':
        logger.warn('ALL defaulting to BESTIARY because thats all that implemented so far.')
        setup_bestiary(target)
    
    elif _type == 'BESTIARY':
        setup_bestiary(target)
    else:
        logger.error('Unrechable block')

def get_cr(maybe_dict) -> dict[str, float]:
    ret = {}
    if isinstance(maybe_dict, dict):
        ret['monster'] = convert_to_float(maybe_dict['cr'])
        ret['lair'] = convert_to_float(maybe_dict['lair'])
    else:
        ret['monster'] = convert_to_float(maybe_dict)
    
    return ret

def get_action_block(actions) -> ActionsBlock:
    items: list[Item] = []
    logger.info(actions)
    for action in actions:
        name = action['name']
        description = ''.join(s for s in action['entries'] if isinstance(s, str))
        sub_items: list[Item] = []
        for entry in (entry for entry in action['entries'] if not isinstance(entry, str)):
            for item in entry.get('items'):
                entry = item.get('entry')
                if entry is None:
                    entry = ' '.join(item['entries'])
                sub_items.append(Item(item['name'], entry, []))

        items.append(Item(name, description, sub_items))
    return ActionsBlock(items)

def handle_action_item_as_dict(sub_obj) -> list[str] | list[Item]:
    if sub_obj['type'] == 'list':
        if all(isinstance(s, str) for s in sub_obj['items']):
            return sub_obj['items']
        has_only_entries_key = all('entries' in item for item in sub_obj['items'])
        if has_only_entries_key:
            return [Item(item['name'], ' '.join(item['entries']), []) for item in sub_obj['items']]
        else:
            return [Item(item['name'], item['entry'], []) for item in sub_obj['items']]
    elif sub_obj['type'] == 'entries':
        if all(isinstance(s, str) for s in sub_obj['entries']):
            return [Item(sub_obj['name'], ' '.join(sub_obj['entries']), [])]
        else:
            name = sub_obj['name']
            description = ''
            sub_items = []
            for e in sub_obj['entries']:
                if isinstance(e, str):
                    description = description + ' ' + e
                else:
                    if e.get('items'):
                        for i in e['items']:
                            sub_item = Item(i['name'], i['entry'], [])
                            sub_items.append(sub_item)
                    elif e.get('type') == 'table':
                        sub_item = Item(e['caption'], e['colLabels'][1] +' (' + e['colLabels'][0] + ')', [])
                        for row in e['rows']:
                            roll = row[0].replace('\\u2013', '-')
                            desc = row[1].replace('"','')
                            sub_item.sub_items.append(Item(roll, desc, []))
                    else:
                        logger.error('No `items` key under sub_obj[top_idx][`entries`][sub_idx]')
            return [Item(name, description, sub_items)]
    else:
        logger.error('sub_obj["type"] neq entries or list')

def create_lair_actions(source: str, actions_list) -> LairActionsBlock:
    desc = ''
    agg = []

    if isinstance(actions_list, dict):
        actions_list = actions_list['items']

    for i in actions_list:
        # actions_list could be a obj and not a list!!
        if isinstance(i, str):
            desc = desc + ' ' + i
        elif isinstance(i, dict):
            agg.extend(handle_action_item_as_dict(i))
        else:
            logger.warn(f'i is typeof({typeof(i)}) which is not supported!!')

    return LairActionsBlock(source, desc, agg)

def handle_non_string_node(node) -> list[Item]:
    if node.get('type') == 'item':
        name = node.get('name')
        desc = ''
        if node.get('entries'):
            desc = ' '.join(node['entries'])
        else:
            desc = node['entry']
        return [Item(name, desc, [])]
    if node.get('type') == 'list' and all(isinstance(i, str) for i in node.get('items')):
        return [Item(node.get('name'), ' '.join(node['items']), [])]
    if node.get('type') == 'list': 
        if node.get('entries'):
            return [handle_non_string_node(i) for i in node['entries'] if not isinstance(i, str)]
        else:
            return [handle_non_string_node(i) for i in node['items'] if not isinstance(i, str)]
    if node.get('type') == 'entries':
        name = node['name']
        desc = ' '.join(s for s in node['entries'] if isinstance(s, str))
        sub_items = [handle_non_string_node(i) for i in node['entries'] if not isinstance(i, str)]
        return [Item(name, desc, sub_items)]
    if node.get('type') == 'table':
        item = Item(node['caption'], node['colLabels'][1] +' (' + node['colLabels'][0] + ')', [])
        for row in node['rows']:
            roll = row[0].replace('\\u2013', '-')
            desc = row[1].replace('"','')
            item.sub_items.append(Item(roll, desc, []))
        return [item]
    else:
        logger.error('node had no type key. im guessing its a nested string?')
    

def create_regional_effects(source: str, regional_effects_list) -> RegionalEffectsBlock:
    desc = ''
    agg = []

    if isinstance(regional_effects_list, dict):
        regional_effects_list = regional_effects_list['items']

    for i in regional_effects_list:
        # TODO regional_effects_list could be a obj and not a list!!
        if isinstance(i, str):
            desc = desc + ' ' + i
        elif isinstance(i, dict):
            agg.extend(handle_non_string_node(i))
        else:
            logger.error(f'i is typeof({typeof(i)}) which is not supported!!')

    return RegionalEffectsBlock(source, desc, agg)

def create_traits(items) -> list[Item]:
    l = []
    for t in items:
        name = t['name']
        desc = ' '.join([s for s in t['entries'] if isinstance(s, str)])
        sub_items = [Item(si['name'], ' '.join(si['entries']), []) for si in t['entries'] if not isinstance(si, str)]
        l.append(Item(name, desc, sub_items))
    return l

def create_ac(ac) -> list[(int, str)]:
    l = []
    for i in ac:
        if isinstance(i, int):
            l.append((i, 'base'))
        elif isinstance(i, dict):
            ac = i['ac']
            if i.get('from'):
                source = ', '.join(i['from'])
            else:
                source = i['condition']
            l.append((ac, source))
    return l


def setup_bestiary(path: Path) -> None:
    target: Path = Path(path) / 'data' / 'bestiary'
    logger.info(target)
    #target = Path.home() / 'repositories' / 'dnd5e-tools' / 'test'

    monsters: list[Monster] = []
    for file in (f for f in target.rglob('*.json') if f.name.startswith('bestiary')):
        logger.info(file)
        data = json.loads(file.read_text(encoding="UTF-8"))
        for entry in data['monster']:
            logger.info(f'creating monster {entry["name"]}')
            if entry.get('cr') is None:
                continue

            alignment = ''.join(entry['alignment']) if entry.get('alignment') else None
            # TODO skip if cr == 'Unknown'
            cr = get_cr(entry['cr'])
            stat_block: StatBlock = StatBlock(entry['str'], entry['dex'], entry['con'], entry['int'], entry['wis'], entry['cha'], )
            
            ac = create_ac(entry['ac'])
            logger.info(ac)

            traits = create_traits(entry['trait']) if entry.get('trait') else None
            
            actions = get_action_block(entry['action']) if entry.get('action') else None
            legendary_actions = get_action_block(entry.get('legendary')) if entry.get('legendary') else None
            variant = entry.get('variant')
            legendary_group_name = None
            if entry.get('legendaryGroup'):
                legendary_group_name = entry.get('legendaryGroup')['name']

            monsters.append(Monster(entry['name'],
                              entry['hp']['average'],
                              stat_block,
                              entry['speed'],
                              alignment,
                              ac,
                              entry['size'],
                              entry.get('languages', []),
                              entry['passive'],
                              entry.get('resist', []),
                              entry.get('immune', []),
                              entry.get('vulnerable', []),
                              entry.get('conditionImmune', []),
                              entry['source'],
                              entry.get('page'),
                              entry['type'],
                              entry['hp']['formula'],
                              entry.get('environment', []),
                              entry.get('save', []),
                              entry.get('skill', []),
                              entry.get('sense', []),
                              cr['monster'],
                              cr.get('lair'),
                              traits,
                              actions,
                              legendary_actions,
                              legendary_group_name,
                              None,
                              None,
                              variant))

    with (target / 'legendarygroups.json').open(encoding='UTF-8') as json_file:
        data = json.load(json_file)
        lair_actions_by_name = {}
        regional_effects_by_name = {}
        for i in data['legendaryGroup']:
            name = i['name']

            if name not in lair_actions_by_name:
                lair_actions_by_name[name] = []

            if name not in regional_effects_by_name:
                regional_effects_by_name[name] = []

            source = i['source']
            for k, v in i.items():
                if k == '_copy':
                    if v['_mod'].get('lairActions'):
                        lair_actions_by_name[name].append(create_lair_actions(source, v['_mod']['lairActions']))
                    if v['_mod'].get('regionalEffects'):
                        regional_effects_by_name[name].append(create_regional_effects(source, v['_mod']['regionalEffects']))
                if k == 'lairActions':
                    lair_actions_by_name[name].append(create_lair_actions(source, v))
                if k == 'regionalEffects':
                    regional_effects_by_name[name].append(create_regional_effects(source, v))
        
        for m in monsters:
            if m.legendary_group_name in lair_actions_by_name:
                logger.info(f'adding lair actions to {m.name} because {m.legendary_group_name} is in lair actions keys')
                m.lair_actions = lair_actions_by_name[m.legendary_group_name]

            if m.legendary_group_name in regional_effects_by_name:
                logger.info(f'adding lair actions to {m.name} because {m.legendary_group_name} is in regional effects keys')
                m.regional_effects = regional_effects_by_name[m.legendary_group_name]

