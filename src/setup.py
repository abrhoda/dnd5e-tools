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
    for action in actions:
        name = action['name']
        description = action['entries'][0]
        sub_items: list[Item] = []
        for entry in (action['entries'][1:] if len(action['entries']) > 1 else []):
            for item in entry.get('items'):
                entry = item.get('entry')
                if entry is None:
                    entry = ' '.join(item['entries'])
                sub_items.append(Item(item['name'], entry, []))

        items.append(Item(name, description, sub_items))
    return ActionsBlock(items)

def handle_item_as_dict(sub_obj) -> list[str] | list[Item]:
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

def create_lair_actions(source: str, actions_list) -> LairActionsBlock:
    desc = ''
    agg = []

    if isinstance(actions_list, dict):
        actions_list = actions_list['items']

    for i in actions_list:
        # json could be a obj
        if isinstance(i, str):
            desc = desc + ' ' + i
        elif isinstance(i, dict):
            agg.append(handle_item_as_dict(i))
        else:
            logger.warn(f'i is typeof({typeof(i)}) which is not supported!!')

    return LairActionsBlock(source, desc, agg)

def handle_node(field) -> list[str] | list[Item]:
    if isinstance(field, str):
        return field
    if field.get('type') == 'table':
        item = Item(field['caption'], field['colLabels'][1] +' (' + field['colLabels'][0] + ')', [])
        for row in field['rows']:
            roll = row[0].replace('\\u2013', '-')
            desc = row[1].replace('"','')
            item.sub_items.append(Item(roll, desc, []))
        return item
    if field.get('name') and field.get('entry'):
        return Item(field['name'], field['entry'], [])
    if field.get('entries'):
        if field.get('name'):
            if all(isinstance(i, str) for i in field['entries']):
                return Item(field['name'], ' '.join(field['entries']), [])
            else:
                desc = ' '.join(s for s in field['entries'] if isinstance(s, str))
                sub = [handle_node(it) for it in field['entries'] if not isinstance(it, str)]
                return Item(field['name'], desc, sub)
        else:
            return ' '.join(field['entries'])

def handle_complex_node(complex_node) -> list[Item]
    if complex_node.get('items'):
        if all(i.get('entry') for i in complex_node['items']):
            return [Item(item['name'], item['entry'], []) for item in complex_node['items']]
    elif complex_node.get('type') == 'table':
        item = Item(complex_node['caption'], complex_node['colLabels'][1] +' (' + complex_node['colLabels'][0] + ')', [])
            roll = row[0].replace('\\u2013', '-')
            desc = row[1].replace('"','')
            item.sub_items.append(Item(roll, desc, []))
            return [item]
    

def handle_non_string_node(node) -> Item
    if node.get('type') == 'list' and all(isinstance(i, str) for i in node.get('items')):
        return Item(node.get('name'), None, node['items'])
    if node.get('type') == 'list':
    if node.get('type') == 'entries':
        name = node['name']
        desc = ' '.join(s for s in node['entries'] if isinstance(s, str))
    

def create_regional_effects(source: str, effects_list) -> RegionalEffectsBlock:
    desc = ''
    agg = []

    #if isinstance(effects_list, dict):
    #    effects_list = effects_list['items']

    for i in effects_list:
        # json could be a obj
        if isinstance(i, str):
            desc = desc + ' ' + i
        elif isinstance(i, dict):
            agg.append(handle_node(i))
        else:
            logger.warn(f'i is typeof({typeof(i)}) which is not supported!!')

    return RegionalEffectsBlock(source, desc, agg)


def setup_bestiary(path: Path) -> None:
    #target: Path = path / 'data' / 'bestiary'
    target = Path.home() / 'repositories' / 'play-together' / 'test'

    monsters: list[Monster] = []
    for file in (f for f in target.rglob('*.json') if f.name.startswith('monster')):
        data = json.loads(file.read_text(encoding="UTF-8"))
        for entry in data['monster']:
            if entry.get('cr') is None:
                continue

            alignment = ''.join(entry['alignment'])
            # TODO skip if cr == 'Unknown'
            cr = get_cr(entry['cr'])
            stat_block: StatBlock = StatBlock(entry['str'], entry['dex'], entry['con'], entry['int'], entry['wis'], entry['cha'], )
            
            ac = entry['ac'][0]
            natural_armor = False
            if isinstance(entry['ac'][0], dict):
                ac = entry['ac'][0]['ac']
                natural_armor = (entry['ac'][0]['from'][0] == "natural armor")
            
            traits = {}
            for trait in entry.get('trait'):
                traits[trait['name']] = ' '.join(trait['entries'])
            
            actions = get_action_block(entry.get('action'))
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
                              natural_armor,
                              entry['size'],
                              entry.get('languages', []),
                              entry['passive'],
                              entry.get('resist', []),
                              entry.get('immune', []),
                              entry.get('vulnerable', []),
                              entry.get('conditionImmune', []),
                              entry['source'],
                              entry['page'],
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
            logger.info(f'top level obj name = {name}')
            for k, v in i.items():
                if k == '_copy':
                    #if v['_mod'].get('lairActions'):
                    #    lair_actions_by_name[name].append(create_lair_actions(source, v['_mod']['lairActions']))
                    if v['_mod'].get('regionalEffects'):
                        logger.info('first')
                        regional_effects_by_name[name].append(create_regional_effects(source, v['_mod']['regionalEffects']))
                #if k == 'lairActions':
                #    lair_actions_by_name[name].append(create_lair_actions(source, v))
                if k == 'regionalEffects':
                    regional_effects_by_name[name].append(create_regional_effects(source, v))

        for key, value in regional_effects_by_name.items():
            logger.info(f'{key}: - {value}')
