$repoRootRelative = "../../";
$repoRoot = (Resolve-Path $PSScriptRoot/$repoRootRelative).Path;

Write-Host "Updating submodules..."
Set-Location $repoRoot
git submodule update --init --recursive
git submodule status

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
