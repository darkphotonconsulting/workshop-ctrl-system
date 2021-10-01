# Example Use-Cases

## GraphQL backend

### GraphQL Query Example: GPIO Data

```graphql
query  {
  allGpios {
    edges {
      node {
        label
        data {
          boardmap {
            wiringPi,
            physicalBoard,
            gpioBcm
          },
          title,
          descr,
          funcs,
          uuid
        }
      }
    }
  }
}
```
