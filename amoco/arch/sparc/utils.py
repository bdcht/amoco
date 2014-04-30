CONDB = {
  0b1000: 'ba',
  0b0000: 'bn',
  0b1001: 'bne',
  0b0001: 'be',
  0b1010: 'bg',
  0b0010: 'ble',
  0b1011: 'bge',
  0b0011: 'bl',
  0b1100: 'bgu',
  0b0100: 'bleu',
  0b1101: 'bcc',
  0b0101: 'bcs',
  0b1110: 'bpos',
  0b0110: 'bneg',
  0b1111: 'bvc',
  0b0111: 'bvs'
}
CONDFB = {
  0b1000: 'fba',
  0b0000: 'fbn',
  0b0111: 'fbu',
  0b0110: 'fbg',
  0b0101: 'fbug',
  0b0100: 'fbl',
  0b0011: 'fbul',
  0b0010: 'fblg',
  0b0001: 'fbne',
  0b1001: 'fbe',
  0b1010: 'fbue',
  0b1011: 'fbge',
  0b1100: 'fbuge',
  0b1101: 'fble',
  0b1110: 'fbule',
  0b1111: 'fbo'
}
CONDCB = {
  0b1000: 'cba',
  0b0000: 'cbn',
  0b0111: 'cb3',
  0b0110: 'cb2',
  0b0101: 'cb23',
  0b0100: 'cb1',
  0b0011: 'cb13',
  0b0010: 'cb12',
  0b0001: 'cb123',
  0b1001: 'cb0',
  0b1010: 'cb03',
  0b1011: 'cb02',
  0b1100: 'cb023',
  0b1101: 'cb01',
  0b1110: 'cb013',
  0b1111: 'cb012'
}
CONDT = {
  0b1000: 'ta',
  0b0000: 'tn',
  0b1001: 'tne',
  0b0001: 'te',
  0b1010: 'tg',
  0b0010: 'tle',
  0b1011: 'tge',
  0b0011: 'tl',
  0b1100: 'tgu',
  0b0100: 'tleu',
  0b1101: 'tcc',
  0b0101: 'tcs',
  0b1110: 'tpos',
  0b0110: 'tneg',
  0b1111: 'tvc',
  0b0111: 'tvs'
}

CONDxB = {'b': CONDB, 'fb': CONDFB, 'cb': CONDCB}

