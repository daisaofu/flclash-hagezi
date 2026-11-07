'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../Script/mihomoScript.js'), 'utf8');
const baseConfig = { proxies: [{ name: '🇺🇸 美国 01', type: 'ss', server: '192.0.2.1', port: 443, cipher: 'aes-128-gcm', password: 'test' }] };
function run(src = source) {
  const context = {};
  vm.runInNewContext(src + '\nglobalThis.__test = { main, ruleOptionsEnable };', context);
  return { context, api: context.__test };
}

assert.equal(source.split('\n')[0], '// FlClash 覆写脚本');
let { api } = run();
let out = api.main(structuredClone(baseConfig));
assert.deepEqual(Array.from(out.rules.slice(0, 3)), [
  'RULE-SET,private,直连', 'RULE-SET,hagezi,REJECT', 'RULE-SET,geolocation-cn,直连',
]);
assert.equal(out['rule-providers'].hagezi.format, 'text');
assert.equal(out['rule-providers'].hagezi.behavior, 'domain');
assert.equal(out['rule-providers'].hagezi.url.endsWith('/hagezi-pro-mini-mihomo.txt'), true);
assert.match(out['rule-providers'].hagezi.url, /daisaofu\/flclash-hagezi/);
assert.equal(out['rule-providers'].hagezi.proxy, '默认代理');
assert.equal(out.tun.stack, 'mixed');
assert.equal(out.ipv6, false);
assert.equal(out.dns.ipv6, false);

({ api } = run(source.replace("  HaGeZiList: 'pro.mini',", "  HaGeZiList: 'light',").replace('  IPv6Enabled: true,', '  IPv6Enabled: false,')));
out = api.main(structuredClone(baseConfig));
assert.equal(out['rule-providers'].hagezi.url.endsWith('/hagezi-light-mihomo.txt'), true);
assert.equal(out.ipv6, false);

({ api } = run(source.replace("  HaGeZiAllowlist: [],", "  HaGeZiAllowlist: ['example.com'],")));
out = api.main(structuredClone(baseConfig));
assert.deepEqual(Array.from(out.rules.slice(0, 4)), [
  'RULE-SET,private,直连', 'DOMAIN,example.com,PASS', 'RULE-SET,hagezi,REJECT', 'RULE-SET,geolocation-cn,直连',
]);
assert.equal(out['proxy-groups'].find(x => x.name === 'AdBlock').proxies.includes('PASS'), true);

({ api } = run(source.replace('  HaGeZi: true,', '  HaGeZi: false,')));
out = api.main(structuredClone(baseConfig));
assert.equal(Boolean(out['rule-providers'].hagezi), false);
assert.equal(out.rules.some(x => x.includes('hagezi')), false);

({ api } = run(source.replace('极简国内外分流模式: false', '极简国内外分流模式: true')));
out = api.main(structuredClone(baseConfig));
assert.equal(Boolean(out['rule-providers'].hagezi), true);
assert.equal(out.rules.includes('RULE-SET,hagezi,REJECT'), true);

assert.throws(() => api.main({ ...structuredClone(baseConfig), 'proxy-providers': { remote: { type: 'http' } } }), /proxy-providers/);
assert.throws(() => run(source.replace("  HaGeZiList: 'pro.mini',", "  HaGeZiList: 'ultimate',")).api.main(structuredClone(baseConfig)), /HaGeZiList/);
assert.throws(() => run(source.replace("  HaGeZiAllowlist: [],", "  HaGeZiAllowlist: ['*.example.com'],")).api.main(structuredClone(baseConfig)), /域名格式无效/);
assert.throws(() => run(source.replace("  TUNStack: 'mixed',", "  TUNStack: 'mips',")).api.main(structuredClone(baseConfig)), /TUNStack/);

console.log('PASS: syntax-compatible FlClash marker');
console.log('PASS: provider, priority, allowlist, toggle, simple mode, input guards');
