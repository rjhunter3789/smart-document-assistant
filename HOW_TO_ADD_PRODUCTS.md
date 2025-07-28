# How to Add Products and Vendors

## Quick Add Format

Edit `products_vendors.json` to add your products and vendors.

### Adding a New Vendor

```json
"Your Vendor Name": {
  "full_name": "Full Company Name",
  "category": "Category Type",
  "products": ["Product 1", "Product 2"],
  "focus": "What they specialize in",
  "keywords": ["keyword1", "keyword2", "keyword3"]
}
```

### Adding a New Product

```json
"Your Product Name": {
  "vendor": "Vendor Name",
  "category": "Product Category",
  "description": "Brief description of what it does",
  "aliases": ["Alternate Name 1", "Acronym"],
  "keywords": ["search term 1", "search term 2"]
}
```

## Example: Adding a Ford Product

```json
"Ford Co-Pilot360": {
  "vendor": "Ford",
  "category": "Safety Technology",
  "description": "Advanced driver-assist technology suite",
  "aliases": ["Co-Pilot 360", "CoPilot360"],
  "keywords": ["safety", "driver assist", "ADAS"]
}
```

## Categories You Might Use

- **AI & Automation** - AI tools, chatbots, automation platforms
- **Marketing Platforms** - Digital marketing, advertising tools
- **CRM Systems** - Customer relationship management
- **Analytics Tools** - Data, reporting, metrics platforms
- **Dealer Tools** - DMS, inventory management, F&I tools
- **Ford Programs** - Official Ford/Lincoln programs
- **Website Solutions** - Website providers, SEO tools

## Benefits

Once added, the AI will:
1. Recognize these products in any query
2. Provide context about what they are
3. Search more accurately for related documents
4. Give better answers based on vendor/product relationships

## Testing

After adding products, test with:
- "Tell me about [Product Name]"
- "What is [Vendor Name]'s solution for..."
- "Compare [Product 1] and [Product 2]"

The AI immediately uses this knowledge - no restart needed!