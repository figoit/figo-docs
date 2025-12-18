# Products Data Structure - MongoDB Schema

## Product Document Schema

```typescript
{
  _id: ObjectId,
  createdAt: Date,
  updatedAt: Date,
  isActive: Boolean,
  name: String,
  description: String,
  keywords: String,
  brandDetails: {
    _id: ObjectId,
    name: String,
  },
  categoryDetails: {
    hierarchy: Array<{
      _id: ObjectId,
      name: String,
      level: Number,
    }>,
    lastCategory: {
      _id: ObjectId,
      name: String,
      level: Number,
      departmentId: ObjectId,
      departmentName: String,
      parentId: ObjectId | null,
      parentName: String | null,
    },
  },
  segments: Array<{
    _id: ObjectId,
    name: String,
    slug: String,
  }>,
  processType: String,
  productType: String,
  registerType: String,
  buId: ObjectId,
  storeReferenceId: String,
  characteristics: Array<{
    key: String,
    value: String
  }>,
  technicalSpecifications: Array<{
    key: String,
    value: String
  }>,
  skus: Array<{
    _id: ObjectId,
    createdAt: Date,
    updatedAt: Date,
    code: String,
    ean: String,
    isActive: Boolean,
    isStoreActive: Boolean,
    isMaster: Boolean,
    segments: Array<{
      _id: ObjectId,
      name: String,
      slug: String,
    }>,
    price: {
      createdAt: Date,
      updatedAt: Date,
      isActive: Boolean,
      saleValue: Decimal128,
      promotionalValue: Decimal128,
      costCurrencyValue: Decimal128,
      storeCurrencyValue: Decimal128,
    },
    attributes: {
      createdAt: Date,
      // Fixed fields - commonly used in queries/filters
      colors: Array<String>,
      // Dynamic attributes - segment-specific
      specifications: Array<{
        key: String,
        value: String,
        type: String,        // "text", "number", "boolean", "select"
        unit: String | null, // "cm", "kg", "V", "W", etc.
        filterable: Boolean, // Can be used as filter in UI
        displayOrder: Number,
      }>,
    },
    images: Array<{
      _id: ObjectId,
      createdAt: Date,
      updatedAt: Date,
      small: String,
      medium: String,
      large: String,
      zoom: String,
      order: Number,
      isMaster: Boolean,
    }>,
  }>,
  elasticsearchId: String,
}
```

## MongoDB Data Types Reference

| Type                 | Description        | Usage                   |
| -------------------- | ------------------ | ----------------------- |
| **ObjectId**   | 12-byte identifier | Unique MongoDB IDs      |
| **Date**       | ISODate timestamp  | Date and time values    |
| **String**     | UTF-8 string       | Text fields             |
| **Boolean**    | true/false         | Binary flags            |
| **Decimal128** | 128-bit decimal    | Precise monetary values |
| **Number**     | 32/64-bit integer  | Numeric values          |
| **Array**      | Ordered list       | Collections of values   |
| **Object**     | Embedded document  | Nested structures       |
| **null**       | Null value         | Optional fields         |

## Field Descriptions

### Root Level Fields

- **`_id`**: Unique product identifier (MongoDB ObjectId)
- **`createdAt`**: Product creation timestamp
- **`updatedAt`**: Last product update timestamp
- **`isActive`**: Product active status flag
- **`name`**: Product name/title
- **`description`**: Detailed product description (supports HTML)
- **`keywords`**: SEO keywords and search metadata
- **`processType`**: Processing type (e.g., "Online", "Offline")
- **`productType`**: Product category type (e.g., "Produto", "Serviço")
- **`registerType`**: Registration method (e.g., "Integracao", "Manual")
- **`buId`**: Business unit identifier reference
- **`storeReferenceId`**: External store/partner product identifier
- **`elasticsearchId`**: Elasticsearch document ID for search indexing

### Brand Information (Denormalized)

- **`brandDetails`**: Embedded brand/manufacturer information
  - **`_id`**: Brand unique identifier
  - **`name`**: Brand/manufacturer name

> **Note:** This is denormalized for read performance. When brand data changes, all related products must be updated.

### Category Information (Denormalized - Flexible Hierarchy)

- **`categoryDetails`**: Embedded category hierarchy with flexible levels
  - **`hierarchy`**: Array representing complete category path from root to leaf
    - **`_id`**: Category unique identifier at this level
    - **`name`**: Category name at this level
    - **`level`**: Hierarchy level (1=root/department, 2, 3, 4, ... N)
  
  - **`lastCategory`**: Quick access to the most specific (leaf) category
    - **`_id`**: Last category unique identifier
    - **`name`**: Last category name
    - **`level`**: Level of this category in hierarchy
    - **`departmentId`**: Root department identifier
    - **`departmentName`**: Root department name
    - **`parentId`**: Immediate parent category identifier (null if level 1)
    - **`parentName`**: Immediate parent category name (null if level 1)

> **Note:** This flexible structure supports N-level hierarchies (not limited to 3 levels).
> - **`hierarchy`** provides full breadcrumb path for navigation
> - **`lastCategory`** optimizes queries for most-specific category filters
> - Denormalized for read performance - requires sync when categories change

#### Hierarchy Examples

**Example 1: Simple 2-Level Hierarchy**
```javascript
// Path: Eletrônicos > Smartphones
categoryDetails: {
  hierarchy: [
    { _id: ObjectId("cat1"), name: "Eletrônicos", level: 1 },
    { _id: ObjectId("cat2"), name: "Smartphones", level: 2 }
  ],
  lastCategory: {
    _id: ObjectId("cat2"),
    name: "Smartphones",
    level: 2,
    departmentId: ObjectId("cat1"),
    departmentName: "Eletrônicos",
    parentId: ObjectId("cat1"),
    parentName: "Eletrônicos"
  }
}
```

**Example 2: Deep 5-Level Hierarchy**
```javascript
// Path: Moda > Feminino > Roupas > Vestidos > Vestidos Longos
categoryDetails: {
  hierarchy: [
    { _id: ObjectId("cat1"), name: "Moda", level: 1 },
    { _id: ObjectId("cat2"), name: "Feminino", level: 2 },
    { _id: ObjectId("cat3"), name: "Roupas", level: 3 },
    { _id: ObjectId("cat4"), name: "Vestidos", level: 4 },
    { _id: ObjectId("cat5"), name: "Vestidos Longos", level: 5 }
  ],
  lastCategory: {
    _id: ObjectId("cat5"),
    name: "Vestidos Longos",
    level: 5,
    departmentId: ObjectId("cat1"),
    departmentName: "Moda",
    parentId: ObjectId("cat4"),
    parentName: "Vestidos"
  }
}
```

**Example 3: Single-Level (Root Only)**
```javascript
// Path: Serviços (no subcategories)
categoryDetails: {
  hierarchy: [
    { _id: ObjectId("cat1"), name: "Serviços", level: 1 }
  ],
  lastCategory: {
    _id: ObjectId("cat1"),
    name: "Serviços",
    level: 1,
    departmentId: ObjectId("cat1"),
    departmentName: "Serviços",
    parentId: null,
    parentName: null
  }
}
```

### Segments Information (Denormalized)

- **`segments`**: Array of segments this product belongs to
  - **`_id`**: Segment unique identifier
  - **`name`**: Segment display name (e.g., "Moda", "Tecnologia")
  - **`slug`**: URL-friendly segment identifier

> **Note:** Products can belong to multiple segments. A product is assigned to a segment through:
> 1. **Category match**: Product's category is linked to the segment
> 2. **Brand match**: Product's brand is linked to the segment
> 3. **SKU match**: Product's SKU is explicitly linked to the segment
>
> This denormalized array improves query performance for segment-based searches. See `segmentStructure.md` for detailed segment management.

### Product Attributes

- **`characteristics`**: Array of product characteristics

  - Key-value pairs for general product features
  - Example: `{key: "ComoUsar", value: "Instruções de uso..."}`
- **`technicalSpecifications`**: Array of technical specifications

  - Key-value pairs for technical details
  - Example: `{key: "Cor", value: "Preta"}`, `{key: "Voltagem", value: "110V"}`

### SKU Structure (Product Variants)

- **`skus`**: Array of product variants/SKUs
  - **`_id`**: SKU unique identifier
  - **`createdAt`**: SKU creation timestamp
  - **`updatedAt`**: SKU last update timestamp
  - **`code`**: Internal SKU code
  - **`ean`**: EAN/barcode number
  - **`isActive`**: SKU active status in the system
  - **`isStoreActive`**: SKU active status from store/partner
  - **`isMaster`**: Flag indicating if this is the master/default SKU
  - **`segments`**: Array of segments this SKU belongs to (can differ from product segments)
    - **`_id`**: Segment unique identifier
    - **`name`**: Segment display name
    - **`slug`**: URL-friendly segment identifier

> **Important**: SKU-level segments enable granular filtering and listing scenarios:
> - **Use Case - Fashion**: Display each color variant as separate item in listings
> - **Inheritance**: If SKU has no segments, it inherits from parent product
> - **Override**: SKU segments can be different/more specific than product segments
> - **Example**: Product in "Moda" segment, but specific SKU also in "Lançamentos" segment

#### SKU Price Object

- **`price`**: Pricing information
  - **`createdAt`**: Price creation timestamp
  - **`updatedAt`**: Price last update timestamp
  - **`isActive`**: Price active status
  - **`saleValue`**: Current sale price (Decimal128)
  - **`promotionalValue`**: Promotional/discounted price (Decimal128)
  - **`costCurrencyValue`**: Cost value in local currency (Decimal128)
  - **`storeCurrencyValue`**: Store/partner currency value (Decimal128)

#### SKU Attributes (Hybrid Dynamic Structure)

- **`attributes`**: SKU-specific attributes using hybrid approach
  - **`createdAt`**: Attributes creation timestamp
  - **`colors`**: Array of available colors (fixed field, heavily used in filters)
  - **`specifications`**: Dynamic array of segment-specific attributes
    - **`key`**: Attribute identifier (e.g., "size", "material", "voltage")
    - **`value`**: Attribute value (stored as string, cast by type)
    - **`type`**: Data type for validation and UI rendering
      - `"text"`: Free text (e.g., "Cotton blend")
      - `"number"`: Numeric value (e.g., "42", "5.2")
      - `"boolean"`: Yes/No values (e.g., "true", "false")
      - `"select"`: Predefined options (e.g., "M", "110V")
    - **`unit`**: Measurement unit if applicable (e.g., "cm", "kg", "V", "W")
    - **`filterable`**: Whether this attribute can be used as search filter
    - **`displayOrder`**: Order for displaying in UI

> **Design Pattern**: This hybrid approach balances performance and flexibility:
> - **Fixed fields** (`colors`) for attributes used in 80% of queries/filters
> - **Dynamic array** (`specifications`) for segment-specific attributes
> - **Indexed searches** on common fields, full-text on dynamic fields
> - **No schema changes** needed when adding new segments/attributes

#### Dynamic Attributes by Segment

**Fashion Segment:**
```javascript
specifications: [
  { key: "size", value: "M", type: "select", unit: null, filterable: true, displayOrder: 1 },
  { key: "material", value: "100% Cotton", type: "text", unit: null, filterable: true, displayOrder: 2 },
  { key: "fit", value: "Slim", type: "select", unit: null, filterable: true, displayOrder: 3 },
  { key: "length", value: "72", type: "number", unit: "cm", filterable: false, displayOrder: 4 },
  { key: "chest", value: "96", type: "number", unit: "cm", filterable: false, displayOrder: 5 },
  { key: "pattern", value: "Solid", type: "select", unit: null, filterable: true, displayOrder: 6 },
  { key: "sleeve", value: "Short", type: "select", unit: null, filterable: true, displayOrder: 7 },
]
```

**Electronics Segment:**
```javascript
specifications: [
  { key: "voltage", value: "110", type: "select", unit: "V", filterable: true, displayOrder: 1 },
  { key: "power", value: "1000", type: "number", unit: "W", filterable: true, displayOrder: 2 },
  { key: "connectivity", value: "WiFi,Bluetooth", type: "text", unit: null, filterable: true, displayOrder: 3 },
  { key: "storage", value: "256", type: "number", unit: "GB", filterable: true, displayOrder: 4 },
  { key: "warranty", value: "12", type: "number", unit: "months", filterable: false, displayOrder: 5 },
]
```

**Home & Kitchen Segment:**
```javascript
specifications: [
  { key: "capacity", value: "5.2", type: "number", unit: "L", filterable: true, displayOrder: 1 },
  { key: "material", value: "Stainless Steel", type: "select", unit: null, filterable: true, displayOrder: 2 },
  { key: "voltage", value: "Bivolt", type: "select", unit: null, filterable: true, displayOrder: 3 },
  { key: "dimensions", value: "30x40x25", type: "text", unit: "cm", filterable: false, displayOrder: 4 },
  { key: "weight", value: "3.5", type: "number", unit: "kg", filterable: false, displayOrder: 5 },
  { key: "dishwasher_safe", value: "true", type: "boolean", unit: null, filterable: true, displayOrder: 6 },
]
```

#### SKU Images

- **`images`**: Array of product images
  - **`_id`**: Image unique identifier
  - **`createdAt`**: Image upload timestamp
  - **`updatedAt`**: Image last update timestamp
  - **`small`**: Small size image URL (59x59)
  - **`medium`**: Medium size image URL (250x250)
  - **`large`**: Large size image URL (500x500)
  - **`zoom`**: Zoom/high-resolution image URL (1000x1000)
  - **`order`**: Display order/position
  - **`isMaster`**: Flag indicating if this is the primary image

## Design Considerations

### Denormalization Strategy

This schema uses **strategic denormalization** for:

- **Brand information**: Reduces need for lookups on product listings
- **Category hierarchy**: Optimizes category-based queries and navigation

**Trade-offs:**

- ✅ **Pros**: Faster reads, fewer joins, better query performance
- ⚠️ **Cons**: Requires update strategy when referenced data changes

**Recommended approach:**

1. Use MongoDB **Change Streams** to listen for brand/category updates
2. Implement background jobs to sync denormalized data
3. Consider using **$merge** in aggregation pipelines for bulk updates

### Indexing Recommendations

```javascript
// Recommended indexes for optimal query performance
db.products.createIndex({ "isActive": 1, "updatedAt": -1 })
db.products.createIndex({ "brandDetails._id": 1 })

// Category indexes - flexible hierarchy
db.products.createIndex({ "categoryDetails.lastCategory._id": 1 })
db.products.createIndex({ "categoryDetails.lastCategory.departmentId": 1 })
db.products.createIndex({ "categoryDetails.lastCategory.parentId": 1 })
db.products.createIndex({ "categoryDetails.hierarchy._id": 1 })
db.products.createIndex({ "categoryDetails.hierarchy.level": 1 })

db.products.createIndex({ "segments._id": 1, "isActive": 1 })
db.products.createIndex({ "segments.slug": 1 })
db.products.createIndex({ "skus.segments._id": 1, "skus.isActive": 1 })
db.products.createIndex({ "skus.segments.slug": 1 })
db.products.createIndex({ "storeReferenceId": 1 })
db.products.createIndex({ "skus.ean": 1 })
db.products.createIndex({ "skus.code": 1 })
db.products.createIndex({ "name": "text", "description": "text", "keywords": "text" })

// Dynamic attributes indexes
db.products.createIndex({ "skus.attributes.colors": 1 })
db.products.createIndex({ "skus.attributes.specifications.key": 1, "skus.attributes.specifications.value": 1 })
db.products.createIndex({ "skus.attributes.specifications.filterable": 1 })
```

### Querying Flexible Category Hierarchy

#### Example: Find Products in Specific Category (Any Level)

```javascript
// Find all products in "Vestidos" category (level 4)
db.products.find({
  "categoryDetails.hierarchy._id": ObjectId("cat4")
})

// Find all products in "Moda" department (level 1)
db.products.find({
  "categoryDetails.lastCategory.departmentId": ObjectId("cat1")
})
```

#### Example: Find Products by Last Category (Most Specific)

```javascript
// Find products in "Vestidos Longos" (leaf category)
db.products.find({
  "categoryDetails.lastCategory._id": ObjectId("cat5")
})

// With aggregation for breadcrumb
db.products.aggregate([
  { $match: { "categoryDetails.lastCategory._id": ObjectId("cat5") }},
  { $project: {
    name: 1,
    breadcrumb: "$categoryDetails.hierarchy.name"
  }}
])
// Result: breadcrumb: ["Moda", "Feminino", "Roupas", "Vestidos", "Vestidos Longos"]
```

#### Example: Find All Subcategories of a Parent

```javascript
// Find all products where parent is "Vestidos" (cat4)
db.products.find({
  "categoryDetails.lastCategory.parentId": ObjectId("cat4")
})
```

#### Example: Filter by Category Level

```javascript
// Find products at specific hierarchy depth (level 3)
db.products.find({
  "categoryDetails.lastCategory.level": 3
})

// Find deep categorized products (level >= 4)
db.products.find({
  "categoryDetails.lastCategory.level": { $gte: 4 }
})
```

#### Example: Build Category Navigation Tree

```javascript
// Get all unique categories at each level for navigation
async function getCategoryTree(departmentId) {
  return await db.products.aggregate([
    { $match: { 
      "categoryDetails.lastCategory.departmentId": departmentId,
      "isActive": true 
    }},
    { $unwind: "$categoryDetails.hierarchy" },
    { $group: {
      _id: {
        categoryId: "$categoryDetails.hierarchy._id",
        level: "$categoryDetails.hierarchy.level"
      },
      name: { $first: "$categoryDetails.hierarchy.name" },
      productCount: { $sum: 1 }
    }},
    { $sort: { "_id.level": 1, "productCount": -1 }}
  ])
}
```

### Querying Dynamic Attributes

#### Example: Filter Products by Size (Fashion)

```javascript
// Find all products with size "M" in Fashion segment
db.products.aggregate([
  { $match: { 
    "segments.slug": "moda",
    "isActive": true 
  }},
  { $unwind: "$skus" },
  { $match: { 
    "skus.isActive": true,
    "skus.attributes.specifications": {
      $elemMatch: {
        key: "size",
        value: "M",
        filterable: true
      }
    }
  }},
  { $project: {
    productName: "$name",
    skuId: "$skus._id",
    price: "$skus.price.saleValue",
    size: {
      $arrayElemAt: [
        "$skus.attributes.specifications.value",
        { $indexOfArray: ["$skus.attributes.specifications.key", "size"] }
      ]
    }
  }}
])
```

#### Example: Multi-Filter Query (Size + Color + Material)

```javascript
// Fashion segment: Size M, Black, Cotton
db.products.aggregate([
  { $match: { "segments.slug": "moda" } },
  { $unwind: "$skus" },
  { $match: {
    "skus.isActive": true,
    "skus.attributes.colors": "black",
    $and: [
      {
        "skus.attributes.specifications": {
          $elemMatch: { key: "size", value: "M" }
        }
      },
      {
        "skus.attributes.specifications": {
          $elemMatch: { 
            key: "material", 
            value: { $regex: "Cotton", $options: "i" }
          }
        }
      }
    ]
  }},
  { $group: {
    _id: "$_id",
    product: { $first: "$$ROOT" },
    matchingSkus: { $push: "$skus" }
  }}
])
```

#### Example: Range Query (Electronics - Power between 500W and 1500W)

```javascript
db.products.aggregate([
  { $match: { "segments.slug": "eletronicos" } },
  { $unwind: "$skus" },
  { $addFields: {
    "skus.powerValue": {
      $convert: {
        input: {
          $arrayElemAt: [
            "$skus.attributes.specifications.value",
            { $indexOfArray: ["$skus.attributes.specifications.key", "power"] }
          ]
        },
        to: "double",
        onError: 0
      }
    }
  }},
  { $match: { 
    "skus.powerValue": { $gte: 500, $lte: 1500 }
  }}
])
```

#### Building Dynamic Filters (UI Generation)

```javascript
// Get all filterable attributes for a segment
async function getSegmentFilters(segmentSlug) {
  const filters = await db.products.aggregate([
    { $match: { 
      "segments.slug": segmentSlug,
      "isActive": true 
    }},
    { $unwind: "$skus" },
    { $unwind: "$skus.attributes.specifications" },
    { $match: { 
      "skus.attributes.specifications.filterable": true 
    }},
    { $group: {
      _id: "$skus.attributes.specifications.key",
      type: { $first: "$skus.attributes.specifications.type" },
      unit: { $first: "$skus.attributes.specifications.unit" },
      values: { $addToSet: "$skus.attributes.specifications.value" },
      count: { $sum: 1 }
    }},
    { $sort: { count: -1 } }
  ])
  
  return filters
}

// Result for Fashion segment:
[
  { _id: "size", type: "select", unit: null, values: ["PP", "P", "M", "G", "GG"], count: 1547 },
  { _id: "material", type: "text", unit: null, values: ["Cotton", "Polyester", ...], count: 1342 },
  { _id: "fit", type: "select", unit: null, values: ["Slim", "Regular", "Oversized"], count: 1198 },
  ...
]

// Frontend uses this to build filter UI dynamically
```

### SKU-Level Segments: Listing vs Detail Views

#### Use Case: Fashion Segment

**Scenario**: Product "Camiseta Nike Básica" with 3 SKUs (White, Black, Red)

**Problem without SKU segments:**
- Listing shows 1 card (product level)
- User doesn't see color options until clicking
- Poor UX for visual-driven categories

**Solution with SKU segments:**

```javascript
// Product Document
{
  "_id": ObjectId("prod123"),
  "name": "Camiseta Nike Básica",
  "segments": [
    { "_id": ObjectId("seg1"), "name": "Moda", "slug": "moda" }
  ],
  "skus": [
    {
      "_id": ObjectId("sku1"),
      "code": "NIKE-WHITE",
      "attributes": { "model": "Branca", "colors": ["white"] },
      "segments": [
        { "_id": ObjectId("seg1"), "name": "Moda", "slug": "moda" }
      ]
    },
    {
      "_id": ObjectId("sku2"),
      "code": "NIKE-BLACK",
      "attributes": { "model": "Preta", "colors": ["black"] },
      "segments": [
        { "_id": ObjectId("seg1"), "name": "Moda", "slug": "moda" }
      ]
    },
    {
      "_id": ObjectId("sku3"),
      "code": "NIKE-RED",
      "attributes": { "model": "Vermelha", "colors": ["red"] },
      "segments": [
        { "_id": ObjectId("seg1"), "name": "Moda", "slug": "moda" },
        { "_id": ObjectId("seg2"), "name": "Lançamentos", "slug": "lancamentos" }
      ]
    }
  ]
}
```

#### Query Strategy

**1. Listing View - Show Each Variant Separately:**

```javascript
// Aggregate to "explode" products by SKU
db.products.aggregate([
  // Match segment at SKU level
  { $match: { "skus.segments.slug": "moda", "isActive": true } },
  
  // Unwind SKUs to create one document per SKU
  { $unwind: "$skus" },
  
  // Filter only SKUs in this segment
  { $match: { "skus.segments.slug": "moda", "skus.isActive": true } },
  
  // Project fields for listing card
  { $project: {
      productId: "$_id",
      productName: "$name",
      skuId: "$skus._id",
      skuCode: "$skus.code",
      skuModel: "$skus.attributes.model",
      colors: "$skus.attributes.colors",
      price: "$skus.price.saleValue",
      promotionalPrice: "$skus.price.promotionalValue",
      mainImage: { $arrayElemAt: ["$skus.images", 0] },
      brandName: "$brandDetails.name"
  }},
  
  // Sort and paginate
  { $sort: { "price": 1 } },
  { $skip: 0 },
  { $limit: 24 }
])

// Result: 3 separate cards
// Card 1: Camiseta Nike Básica - Branca
// Card 2: Camiseta Nike Básica - Preta
// Card 3: Camiseta Nike Básica - Vermelha
```

**2. Detail View - Show Product with SKU Selector:**

```javascript
// Get full product with all SKUs
db.products.findOne(
  { "_id": ObjectId("prod123") },
  {
    // Return all fields for detailed view
  }
)

// Frontend groups SKUs by attributes
// Shows: "Camiseta Nike Básica"
// Color selector: ○ White ○ Black ○ Red
// Each color shows its own price
```

**3. Fallback Strategy - SKU Inherits Product Segments:**

```javascript
// Application logic to get effective segments
function getEffectiveSegments(product, sku) {
  // If SKU has segments defined, use them
  if (sku.segments && sku.segments.length > 0) {
    return sku.segments;
  }
  
  // Otherwise, inherit from product
  return product.segments || [];
}

// Use in queries
db.products.aggregate([
  { $unwind: "$skus" },
  { $addFields: {
    "skus.effectiveSegments": {
      $cond: {
        if: { $gt: [{ $size: { $ifNull: ["$skus.segments", []] } }, 0] },
        then: "$skus.segments",
        else: "$segments"
      }
    }
  }},
  { $match: { "skus.effectiveSegments._id": ObjectId("seg1") } }
])
```

#### Benefits Summary

| Aspect | Without SKU Segments | With SKU Segments |
|--------|---------------------|-------------------|
| **Listing View** | 1 card per product | 1 card per SKU variant |
| **Visual Discovery** | Click to see options | See all options immediately |
| **Filter Precision** | Product-level only | SKU-level granularity |
| **Fashion UX** | Poor (color hidden) | Excellent (color visible) |
| **Flexibility** | All SKUs same segments | Each SKU can differ |
| **Query Speed** | Fast | Fast (with proper indexes) |

#### Best Practices

1. **Always set SKU segments** for visual-driven categories (Fashion, Home Decor)
2. **Inherit from product** for non-visual categories (Electronics, Books)
3. **Use aggregation** for listing views with proper pagination
4. **Cache results** for popular segments to reduce database load
5. **Update both levels** when segment assignment changes

### Boolean Naming Convention

This schema follows the convention of prefixing boolean fields with **`is`**:

- `isActive` instead of `active` or `activeStatus`
- `isMaster` instead of `master`
- `isStoreActive` instead of `storeActiveStatus`

This makes the code more readable and clearly indicates boolean values.

### Price Precision

All monetary values use **`Decimal128`** type to ensure:

- Precise decimal calculations
- No floating-point errors
- Compliance with financial requirements

## Example Document

```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "createdAt": ISODate("2024-01-15T10:30:00Z"),
  "updatedAt": ISODate("2024-12-18T09:00:00Z"),
  "isActive": true,
  "name": "Fritadeira Sem Óleo Air Fryer Philco Jumbo 5,2L - Preta",
  "description": "Uma vida mais saudável...",
  "keywords": "fritadeira, air fryer, philco",
  "brandDetails": {
    "_id": ObjectId("507f191e810c19729de860ea"),
    "name": "Philco"
  },
  "categoryDetails": {
    "hierarchy": [
      {
        "_id": ObjectId("507f191e810c19729de860eb"),
        "name": "Casa e Cozinha",
        "level": 1
      },
      {
        "_id": ObjectId("507f191e810c19729de860ec"),
        "name": "Eletroportáteis",
        "level": 2
      },
      {
        "_id": ObjectId("507f191e810c19729de860ed"),
        "name": "Fritadeiras",
        "level": 3
      }
    ],
    "lastCategory": {
      "_id": ObjectId("507f191e810c19729de860ed"),
      "name": "Fritadeiras",
      "level": 3,
      "departmentId": ObjectId("507f191e810c19729de860eb"),
      "departmentName": "Casa e Cozinha",
      "parentId": ObjectId("507f191e810c19729de860ec"),
      "parentName": "Eletroportáteis"
    }
  },
  "segments": [
    {
      "_id": ObjectId("507f191e810c19729de860ef"),
      "name": "Casa e Cozinha",
      "slug": "casa-cozinha"
    },
    {
      "_id": ObjectId("507f191e810c19729de860f0"),
      "name": "Eletroportáteis",
      "slug": "eletroportateis"
    }
  ],
  "processType": "Online",
  "productType": "Produto",
  "registerType": "Integracao",
  "buId": ObjectId("507f191e810c19729de860ed"),
  "storeReferenceId": "9157872",
  "characteristics": [
    { "key": "ComoUsar", "value": "Instruções de uso..." }
  ],
  "technicalSpecifications": [
    { "key": "Cor", "value": "Preta" },
    { "key": "Capacidade", "value": "5,2L" }
  ],
  "skus": [
    {
      "_id": ObjectId("507f191e810c19729de860ee"),
      "code": "12729700",
      "ean": "7891356067013",
      "isActive": true,
      "isStoreActive": true,
      "isMaster": true,
      "segments": [
        {
          "_id": ObjectId("507f191e810c19729de860ef"),
          "name": "Casa e Cozinha",
          "slug": "casa-cozinha"
        },
        {
          "_id": ObjectId("507f191e810c19729de860f0"),
          "name": "Eletroportáteis",
          "slug": "eletroportateis"
        }
      ],
      "price": {
        "saleValue": Decimal128("379.90"),
        "promotionalValue": Decimal128("299.90")
      },
      "attributes": {
        "colors": ["black"],
        "specifications": [
          { "key": "voltage", "value": "110", "type": "select", "unit": "V", "filterable": true, "displayOrder": 1 },
          { "key": "power", "value": "1000", "type": "number", "unit": "W", "filterable": true, "displayOrder": 2 },
          { "key": "capacity", "value": "5.2", "type": "number", "unit": "L", "filterable": true, "displayOrder": 3 },
          { "key": "material", "value": "Plastic", "type": "select", "unit": null, "filterable": true, "displayOrder": 4 },
          { "key": "dimensions", "value": "30x40x32", "type": "text", "unit": "cm", "filterable": false, "displayOrder": 5 },
          { "key": "weight", "value": "4.2", "type": "number", "unit": "kg", "filterable": false, "displayOrder": 6 },
          { "key": "timer", "value": "true", "type": "boolean", "unit": null, "filterable": true, "displayOrder": 7 },
          { "key": "warranty", "value": "12", "type": "number", "unit": "months", "filterable": false, "displayOrder": 8 }
        ]
      }
    },
    {
      "_id": ObjectId("507f191e810c19729de860ff"),
      "code": "12729701",
      "ean": "7891356067020",
      "isActive": true,
      "isStoreActive": true,
      "isMaster": false,
      "segments": [
        {
          "_id": ObjectId("507f191e810c19729de860ef"),
          "name": "Casa e Cozinha",
          "slug": "casa-cozinha"
        },
        {
          "_id": ObjectId("507f191e810c19729de860f0"),
          "name": "Eletroportáteis",
          "slug": "eletroportateis"
        },
        {
          "_id": ObjectId("507f191e810c19729de860f1"),
          "name": "Ofertas",
          "slug": "ofertas"
        }
      ],
      "price": {
        "saleValue": Decimal128("379.90"),
        "promotionalValue": Decimal128("249.90")
      },
      "attributes": {
        "colors": ["black"],
        "specifications": [
          { "key": "voltage", "value": "220", "type": "select", "unit": "V", "filterable": true, "displayOrder": 1 },
          { "key": "power", "value": "1000", "type": "number", "unit": "W", "filterable": true, "displayOrder": 2 },
          { "key": "capacity", "value": "5.2", "type": "number", "unit": "L", "filterable": true, "displayOrder": 3 },
          { "key": "material", "value": "Plastic", "type": "select", "unit": null, "filterable": true, "displayOrder": 4 },
          { "key": "dimensions", "value": "30x40x32", "type": "text", "unit": "cm", "filterable": false, "displayOrder": 5 },
          { "key": "weight", "value": "4.2", "type": "number", "unit": "kg", "filterable": false, "displayOrder": 6 },
          { "key": "timer", "value": "true", "type": "boolean", "unit": null, "filterable": true, "displayOrder": 7 },
          { "key": "warranty", "value": "12", "type": "number", "unit": "months", "filterable": false, "displayOrder": 8 }
        ]
      }
    }
  ],
  "elasticsearchId": "9e8bd30c3a37ebd5"
}
```

### Example Document - Fashion Product

```json
{
  "_id": ObjectId("607f1f77bcf86cd799439022"),
  "createdAt": ISODate("2024-06-10T14:20:00Z"),
  "updatedAt": ISODate("2024-12-18T09:00:00Z"),
  "isActive": true,
  "name": "Camiseta Nike Sportswear Essential Feminina",
  "description": "Camiseta básica de algodão com caimento moderno e confortável...",
  "keywords": "camiseta, nike, feminina, algodao, basica",
  "brandDetails": {
    "_id": ObjectId("607f191e810c19729de860fa"),
    "name": "Nike"
  },
  "categoryDetails": {
    "hierarchy": [
      {
        "_id": ObjectId("607f191e810c19729de860fb"),
        "name": "Moda",
        "level": 1
      },
      {
        "_id": ObjectId("607f191e810c19729de860fc"),
        "name": "Feminino",
        "level": 2
      },
      {
        "_id": ObjectId("607f191e810c19729de860fd"),
        "name": "Roupas",
        "level": 3
      },
      {
        "_id": ObjectId("607f191e810c19729de860fe"),
        "name": "Camisetas",
        "level": 4
      },
      {
        "_id": ObjectId("607f191e810c19729de860ff"),
        "name": "Camisetas Básicas",
        "level": 5
      }
    ],
    "lastCategory": {
      "_id": ObjectId("607f191e810c19729de860ff"),
      "name": "Camisetas Básicas",
      "level": 5,
      "departmentId": ObjectId("607f191e810c19729de860fb"),
      "departmentName": "Moda",
      "parentId": ObjectId("607f191e810c19729de860fe"),
      "parentName": "Camisetas"
    }
  },
  "segments": [
    {
      "_id": ObjectId("607f191e810c19729de860fe"),
      "name": "Moda",
      "slug": "moda"
    },
    {
      "_id": ObjectId("607f191e810c19729de860ff"),
      "name": "Feminino",
      "slug": "feminino"
    }
  ],
  "processType": "Online",
  "productType": "Produto",
  "registerType": "Integracao",
  "buId": ObjectId("607f191e810c19729de86100"),
  "storeReferenceId": "NIKE-ESS-FEM",
  "characteristics": [
    { "key": "ComoLavar", "value": "Lavar à mão ou em ciclo delicado" }
  ],
  "technicalSpecifications": [
    { "key": "Composição", "value": "100% Algodão" },
    { "key": "Origem", "value": "Importado" }
  ],
  "skus": [
    {
      "_id": ObjectId("607f191e810c19729de86101"),
      "code": "NIKE-ESS-WHT-M",
      "ean": "7891234567890",
      "isActive": true,
      "isStoreActive": true,
      "isMaster": true,
      "segments": [
        {
          "_id": ObjectId("607f191e810c19729de860fe"),
          "name": "Moda",
          "slug": "moda"
        },
        {
          "_id": ObjectId("607f191e810c19729de860ff"),
          "name": "Feminino",
          "slug": "feminino"
        }
      ],
      "price": {
        "saleValue": Decimal128("89.90"),
        "promotionalValue": Decimal128("79.90")
      },
      "attributes": {
        "colors": ["white"],
        "specifications": [
          { "key": "size", "value": "M", "type": "select", "unit": null, "filterable": true, "displayOrder": 1 },
          { "key": "material", "value": "100% Cotton", "type": "text", "unit": null, "filterable": true, "displayOrder": 2 },
          { "key": "fit", "value": "Regular", "type": "select", "unit": null, "filterable": true, "displayOrder": 3 },
          { "key": "neckline", "value": "Crew Neck", "type": "select", "unit": null, "filterable": true, "displayOrder": 4 },
          { "key": "sleeve", "value": "Short", "type": "select", "unit": null, "filterable": true, "displayOrder": 5 },
          { "key": "pattern", "value": "Solid", "type": "select", "unit": null, "filterable": true, "displayOrder": 6 },
          { "key": "length", "value": "65", "type": "number", "unit": "cm", "filterable": false, "displayOrder": 7 },
          { "key": "chest", "value": "96", "type": "number", "unit": "cm", "filterable": false, "displayOrder": 8 },
          { "key": "care", "value": "Machine washable", "type": "text", "unit": null, "filterable": false, "displayOrder": 9 }
        ]
      }
    },
    {
      "_id": ObjectId("607f191e810c19729de86102"),
      "code": "NIKE-ESS-BLK-M",
      "ean": "7891234567891",
      "isActive": true,
      "isStoreActive": true,
      "isMaster": false,
      "segments": [
        {
          "_id": ObjectId("607f191e810c19729de860fe"),
          "name": "Moda",
          "slug": "moda"
        },
        {
          "_id": ObjectId("607f191e810c19729de860ff"),
          "name": "Feminino",
          "slug": "feminino"
        },
        {
          "_id": ObjectId("607f191e810c19729de86103"),
          "name": "Best Sellers",
          "slug": "best-sellers"
        }
      ],
      "price": {
        "saleValue": Decimal128("89.90"),
        "promotionalValue": Decimal128("0")
      },
      "attributes": {
        "colors": ["black"],
        "specifications": [
          { "key": "size", "value": "M", "type": "select", "unit": null, "filterable": true, "displayOrder": 1 },
          { "key": "material", "value": "100% Cotton", "type": "text", "unit": null, "filterable": true, "displayOrder": 2 },
          { "key": "fit", "value": "Regular", "type": "select", "unit": null, "filterable": true, "displayOrder": 3 },
          { "key": "neckline", "value": "Crew Neck", "type": "select", "unit": null, "filterable": true, "displayOrder": 4 },
          { "key": "sleeve", "value": "Short", "type": "select", "unit": null, "filterable": true, "displayOrder": 5 },
          { "key": "pattern", "value": "Solid", "type": "select", "unit": null, "filterable": true, "displayOrder": 6 },
          { "key": "length", "value": "65", "type": "number", "unit": "cm", "filterable": false, "displayOrder": 7 },
          { "key": "chest", "value": "96", "type": "number", "unit": "cm", "filterable": false, "displayOrder": 8 },
          { "key": "care", "value": "Machine washable", "type": "text", "unit": null, "filterable": false, "displayOrder": 9 }
        ]
      }
    },
    {
      "_id": ObjectId("607f191e810c19729de86104"),
      "code": "NIKE-ESS-WHT-G",
      "ean": "7891234567892",
      "isActive": true,
      "isStoreActive": true,
      "isMaster": false,
      "segments": [
        {
          "_id": ObjectId("607f191e810c19729de860fe"),
          "name": "Moda",
          "slug": "moda"
        },
        {
          "_id": ObjectId("607f191e810c19729de860ff"),
          "name": "Feminino",
          "slug": "feminino"
        }
      ],
      "price": {
        "saleValue": Decimal128("89.90"),
        "promotionalValue": Decimal128("79.90")
      },
      "attributes": {
        "colors": ["white"],
        "specifications": [
          { "key": "size", "value": "G", "type": "select", "unit": null, "filterable": true, "displayOrder": 1 },
          { "key": "material", "value": "100% Cotton", "type": "text", "unit": null, "filterable": true, "displayOrder": 2 },
          { "key": "fit", "value": "Regular", "type": "select", "unit": null, "filterable": true, "displayOrder": 3 },
          { "key": "neckline", "value": "Crew Neck", "type": "select", "unit": null, "filterable": true, "displayOrder": 4 },
          { "key": "sleeve", "value": "Short", "type": "select", "unit": null, "filterable": true, "displayOrder": 5 },
          { "key": "pattern", "value": "Solid", "type": "select", "unit": null, "filterable": true, "displayOrder": 6 },
          { "key": "length", "value": "68", "type": "number", "unit": "cm", "filterable": false, "displayOrder": 7 },
          { "key": "chest", "value": "104", "type": "number", "unit": "cm", "filterable": false, "displayOrder": 8 },
          { "key": "care", "value": "Machine washable", "type": "text", "unit": null, "filterable": false, "displayOrder": 9 }
        ]
      }
    }
  ],
  "elasticsearchId": "nike-ess-fem-2024"
}
```
