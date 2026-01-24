$repoRootRelative = "../../";
$repoRoot = (Resolve-Path $PSScriptRoot/$repoRootRelative).Path;

docker build `
    -f $repoRoot/docs/build/gif-builder.dockerfile `
    -t vhs-robotunused `
    .

docker run `
    -it `
    --rm `
    -v ${repoRoot}:/app `
    vhs-robotunused `
    /app/docs/build/gif-builder.sh;
