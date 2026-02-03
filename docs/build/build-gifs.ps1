$repoRootRelative = "../../";
$repoRoot = (Resolve-Path $PSScriptRoot/$repoRootRelative).Path;

Write-Host "Updating submodules..."
Set-Location $repoRoot
git submodule update --init --recursive
git submodule status

docker ps
If ($LASTEXITCODE -ne 0) {
    # Docker is likely not installed or not running
    Exit 1
}

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
