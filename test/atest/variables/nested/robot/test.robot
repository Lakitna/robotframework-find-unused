*** Variables ***
${helloWorld}       Hello Universe!
${place}            World
${greeting}         hello
${greet}            ${greeting}
${hello1}           Hello Universe!
${helloTrue}        Hello Universe!
${hw}               helloWorld
${h}                ${hw}

${abc}              abcdefg
${easyAs${abc}}     lorum


*** Keywords ***
My Amazing Keyword
    Log    ${helloWorld}
    Log    ${hello${place}}
    Log    ${${greeting}${place}}
    Log    ${${hw}}
    Log    ${${h}}
    Log    ${${greeting}World}
    Log    ${${greet}World}

    Log    ${hello${1}}
    Log    ${hello${True}}

    Log    ${helloUniverse}
    Log    ${hello${foo}}
    Log    ${hello${place}.lower()}

    Log    ${easyAs${abc}}
    Log    ${easyAsabcdefg}
