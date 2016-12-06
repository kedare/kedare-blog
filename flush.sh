set -e # Fail fast

DISTRIBUTION_ID=ERJ5SLWSC01VQ
BUCKET_NAME=blog.kedare.net

# Invalidate everything
aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/index.html" "/" "/page/*" "/blog/*" "/images/*" "/tags/*"
