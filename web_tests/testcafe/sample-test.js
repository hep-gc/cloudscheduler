import { Selector } from 'testcafe';

fixture `Sample Tests`
    .page `https://google.com`;

const search_bar = Selector('input').withAttribute('name', 'q')

test('Canary test', async t => {
    await t.expect(true).eql(true);
});

test('Finding search bar', async t => {
    await t
        .click(search_bar)
});

test('Typing in the search bar', async t => {
    await t
        .typeText(search_bar, 'cloudscheduler')
});

test('Searching', async t => {
    await t
        .typeText(search_bar, 'cloudscheduler')
        .pressKey('enter')
});
