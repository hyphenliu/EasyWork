import IPy


def isIp(address):
    try:
        IPy.IP(address)
        return True
    except Exception as e:
        return False


def complateAccessList(device, originalIP, mask, distinateIP, port):
    data = ''
    errors = {'originalIP': '', 'mask': '', 'distinateIP': '', 'port': ''}
    originalIP = originalIP.split()
    distinateIP = distinateIP.split()

    if not isIp(mask):
        errors['mask'] = mask
        return data, errors

    if len(port.split()) > 1:
        port_str = ' range '
    else:
        port_str = ' eq '

    for o in originalIP:
        if not isIp(o):
            if errors['originalIP']:
                errors['originalIP'] = errors['originalIP'] + ',' + o
            else:
                errors['originalIP'] = o
            continue
        for d in distinateIP:
            if not isIp(d):
                if errors['distinateIP']:
                    errors['distinateIP'] = errors['originalIP'] + ',' + d
                else:
                    errors['distinateIP'] = d
                continue
            if device == 'CISCO':
                accesslist_str = 'access-list outside extended permit tcp ' + str(o) + ' ' + str(mask) + ' host ' + str(
                    d) + port_str + ' ' + str(port)
            elif device in ['H3C', 'huawei']:
                accesslist_str = 'rule permit tcp source ' + str(o) + ' ' + str(mask) + ' destination ' + str(
                    d) + port_str + ' ' + str(port)
            else:
                accesslist_str = '请选择厂商'
            data = data + '<p>' + accesslist_str + '</p>'
    return data, errors
