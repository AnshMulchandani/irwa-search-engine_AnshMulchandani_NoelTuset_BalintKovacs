# RAG comparison: baseline vs improved

Model: `llama-3.1-8b-instant`. Mode: dry run (no LLM calls). Retrieval: Part 2 TF-IDF, AND semantics, top 20.

## `women tshirt round neck cotton`
*common query, thousands of matches*

- Baseline retrieval (raw query): **20** products
- Improved retrieval (query `women tshirt round neck cotton`): **20** products, **8** shown to the LLM after de-duplication and constraints

**Baseline answer**

```
(dry run)
```

**Improved answer**

```
(dry run: LLM would be called with the prompt below)
```

<details><summary>What each LLM sees</summary>

Baseline context:
```
- PID: TSHFNFTHMZDWWJZ5, Title: Solid Women Round Neck Orange T-Shirt
- PID: TSHFKPFATE4SH5JF, Title: Printed Women Round Neck Multicolor T-Shirt
- PID: TSHFKPF9W5HKJMD4, Title: Printed Women Round Neck White T-Shirt
- PID: TSHFV9YCYTZBB2DG, Title: Printed Women Round Neck Black T-Shirt
- PID: TSHFVXGQZTFPMGMR, Title: Printed Women Round Neck White T-Shirt
- PID: TSHFVXGQ9ZMAWFND, Title: Printed Women Round Neck White T-Shirt
- PID: TSHFVXGQ73ZRG9AW, Title: Printed Women Round Neck Blue T-Shirt
- PID: TSHFWTTXNXYGWVFY, Title: Printed Women Round Neck Multicolor T-Shirt
- PID: TSHFME2EVKH9MMGK, Title: Solid Women Round Neck Orange T-Shirt
- PID: TSHFME2ECMZVSMPS, Title: Solid Women Round Neck White T-Shirt
- PID: TSHFWTTXZDHFAEYZ, Title: Printed Women Round Neck Black T-Shirt
- PID: TSHFGK3S4UZZMFC2, Title: Checkered Women Round Neck Beige T-Shirt
- PID: TSHFGK3FYD6Y5EDS, Title: Checkered Women Round Neck Beige T-Shirt
- PID: TSHFKPF9BHEBCH7F, Title: Printed Women Round Neck Grey T-Shirt
- PID: TSHFXMHGUTBAZHKF, Title: Solid Women Round Neck Orange T-Shirt
- PID: TSHFGK3SGWTFWTZP, Title: Checkered Women Round Neck White T-Shirt
- PID: TSHFME2EFHGHJCFY, Title: Color Block Women Round Neck Pink T-Shirt
- PID: TSHFDYRDGKHXY52Z, Title: Solid Women Round Neck White T-Shirt
- PID: TSHFYKYMZCRVBNRK, Title: Solid Women Round Neck Orange T-Shirt
- PID: TSHFGK3YQT4YNQHB, Title: Checkered Women Round Neck Grey T-Shirt
```
Improved prompt:
```
## User request
women tshirt round neck cotton

## What the user asked for, read from the request
no price or rating limits

## Retrieved products (ranked by our search engine, best match first)
[1] PID TSHFNFTHMZDWWJZ5 | Solid Women Round Neck Orange T-Shirt
    Brand: T10 Spor | Price: ₹449 (was ₹899, 50% off) | Rating: 2.3/5 | in stock
    Ideal For: Women | Fabric: Cotton Blend | Fit: Slim | Pattern: Solid | Sleeve: Half Sleeve | Neck Type: Round Neck
    Description: orange tshirts, tshirts. round neck tshirts, round neck tshirts
[2] PID TSHFKPFATE4SH5JF | Printed Women Round Neck Multicolor T-Shirt
    Brand: Amp | Price: ₹349 (was ₹999, 65% off) | Rating: 3.4/5 | in stock
    Ideal For: Women | Fabric: Cotton Blend | Fit: Regular | Pattern: Printed | Sleeve: Full Sleeve | Neck Type: Round Neck
    Description: Multi Kintted Cotton Solid Round NeckFull sleeve Regular Fit Women Casual T-shirts
[3] PID TSHFKPF9W5HKJMD4 | Printed Women Round Neck White T-Shirt
    Brand: Amp | Price: ₹349 (was ₹999, 65% off) | Rating: 3.4/5 | in stock
    Ideal For: Women | Fabric: Cotton Blend | Fit: Regular | Pattern: Printed | Sleeve: Full Sleeve | Neck Type: Round Neck
    Description: White Kintted Cotton Solid Round NeckFull sleeve Regular Fit Women Casual T-shirts
[4] PID TSHFV9YCYTZBB2DG | Printed Women Round Neck Black T-Shirt
    Brand: She | Price: ₹349 (was ₹999, 65% off) | Rating: 3.0/5 | in stock
    Ideal For: Women | Fabric: Cotton Blend | Fit: Slim | Pattern: Printed | Sleeve: Short Sleeve | Neck Type: Round Neck
    Description: You will always be the center of attraction of any gathering by this trendy t-shirt.This t-shirt will add extra class to your looks.This can be a perfect selection for you.
[5] PID TSHFVXGQZTFPMGMR | Printed Women Round Neck White T-Shirt
    Brand: MASH UNLIMIT | Price: ₹329 (was ₹799, 58% off) | Rating: 3.2/5 | in stock
    Ideal For: Women | Fabric: Pure Cotton | Fit: Slim | Pattern: Printed | Sleeve: Half Sleeve | Neck Type: Round Neck
    Description: Women White Round Neck Cotton T-shirt
[6] PID TSHFVXGQ73ZRG9AW | Printed Women Round Neck Blue T-Shirt
    Brand: MASH UNLIMIT | Price: ₹329 (was ₹799, 58% off) | Rating: 3.2/5 | in stock
    Ideal For: Women | Fabric: Pure Cotton | Fit: Slim | Pattern: Printed | Sleeve: Half Sleeve | Neck Type: Round Neck
    Description: Women Blue Round Neck Cotton T-shirt
[7] PID TSHFWTTXNXYGWVFY | Printed Women Round Neck Multicolor T-Shirt
    Brand: Amp | Price: ₹299 (was ₹999, 70% off) | Rating: 3.4/5 | in stock
    Ideal For: Women | Fabric: Cotton Blend | Fit: Regular | Pattern: Printed | Sleeve: Half Sleeve | Neck Type: Round Neck
    Description: Fall in love with the soft texture adorning this Mehroon T-shirt from the house of Aff Garment. Your skin will love the feel of this T-shirt.
[8] PID TSHFME2EVKH9MMGK | Solid Women Round Neck Orange T-Shirt
    Brand: Steenb | Price: ₹449 (was ₹899, 50% off) | Rating: 3.7/5 | in stock
    Ideal For: Women | Fabric: Pure Cotton | Fit: Slim | Pattern: Solid | Sleeve: Short Sleeve | Neck Type: Round Neck
    Description: Steenbok Women's Short Sleeves Round Neck Tshirt

## Instructions
1. Check each product against the request: product type, gender, colour, material and any price or rating limit.
2. Pick the single best product. Prefer, in this order: matches the request, in stock, higher rating, better price.
3. Answer in this exact format, at most 120 words:
- Best Product: [PID] [title]
- Why: one or two sentences that cite the facts above (price, discount, rating, material, fit).
- Alternative: [PID] [title], and the trade-off compared with the best product (for example cheaper but lower rated). Leave out if none.
- Note: only if important information is missing (for example no rating listed).
4. Use only PIDs from the list above.
5. If no product matches the request, answer with exactly: "There are no good products that fit the request based on the retrieved results."

```
</details>

## `ecko unl printed sweatshirt`
*brand query*

- Baseline retrieval (raw query): **18** products
- Improved retrieval (query `ecko unl printed sweatshirt`): **18** products, **8** shown to the LLM after de-duplication and constraints

**Baseline answer**

```
(dry run)
```

**Improved answer**

```
(dry run: LLM would be called with the prompt below)
```

<details><summary>What each LLM sees</summary>

Baseline context:
```
- PID: SWSFZEQEMGUPEM3E, Title: Full Sleeve Printed Women Sweatshirt
- PID: SWSFY38ADYPVZHYZ, Title: Full Sleeve Printed Women Sweatshirt
- PID: SWSFXV6GTKRN9XKH, Title: Full Sleeve Printed Men Sweatshirt
- PID: SWSFXV6GFYTRSZJA, Title: Full Sleeve Printed Men Sweatshirt
- PID: SWSFV5JNDCDYTNQY, Title: Full Sleeve Printed Women Sweatshirt
- PID: SWSFY382UZHFBCNB, Title: Full Sleeve Printed Women Sweatshirt
- PID: SWSFXV6FKYFF35EW, Title: Full Sleeve Printed Women Sweatshirt
- PID: SWSFY36JNHCKZHZT, Title: Full Sleeve Printed Men Sweatshirt
- PID: SWSFY36JHZUBSHEQ, Title: Full Sleeve Printed Women Sweatshirt
- PID: SWSFY36HVGCV8ZKW, Title: Full Sleeve Printed Women Sweatshirt
- PID: SWSFZEQEGPDK9GUB, Title: Full Sleeve Printed Women Sweatshirt
- PID: SWSFY36HNVD3DUBF, Title: Full Sleeve Printed Men Sweatshirt
- PID: SWSFZEQEUMCKMF7T, Title: Full Sleeve Printed Men Sweatshirt
- PID: SWSFZEQEQ2HKYADS, Title: Full Sleeve Graphic Print Men Sweatshirt
- PID: SWSFXV6GQJNCFJZV, Title: Full Sleeve Graphic Print Men Sweatshirt
- PID: SWSFV5JNFW5HZQWY, Title: Full Sleeve Printed Women Sweatshirt
- PID: SWSFV5JN3KHMCDAF, Title: Full Sleeve Printed Men Sweatshirt
- PID: SWSFV5JN5UCWNBHS, Title: Full Sleeve Printed Men Sweatshirt
```
Improved prompt:
```
## User request
ecko unl printed sweatshirt

## What the user asked for, read from the request
no price or rating limits

## Retrieved products (ranked by our search engine, best match first)
[1] PID SWSFZEQEMGUPEM3E | Full Sleeve Printed Women Sweatshirt
    Brand: ECKO Unl | Price: ₹758 (was ₹2,299, 67% off) | Rating: 2.5/5 | in stock
    Fabric: Cotton Blend | Pattern: Printed | Color: Multicolor | Sleeve: Full Sleeve | Neck: Hooded Neck | Occasion: Casual
    Description: ECKO Unltd Solid French terry Regular Fit BLACK/ROYAL/WHITE Sweat Shirt
[2] PID SWSFY38ADYPVZHYZ | Full Sleeve Printed Women Sweatshirt
    Brand: ECKO Unl | Price: ₹703 (was ₹2,199, 68% off) | Rating: 3.6/5 | in stock
    Fabric: Cotton Blend | Pattern: Printed | Color: Multicolor | Sleeve: Full Sleeve | Neck: High Neck | Occasion: Casual
[3] PID SWSFXV6GTKRN9XKH | Full Sleeve Printed Men Sweatshirt
    Brand: ECKO Unl | Price: ₹724 (was ₹1,449, 50% off) | Rating: 2.5/5 | in stock
    Fabric: Cotton Blend | Pattern: Printed | Color: Maroon | Sleeve: Full Sleeve | Neck: Round Neck | Occasion: Casual
[4] PID SWSFV5JNDCDYTNQY | Full Sleeve Printed Women Sweatshirt
    Brand: ECKO Unl | Price: ₹791 (was ₹1,099, 28% off) | Rating: 2.5/5 | in stock
    Fabric: Cotton Blend | Pattern: Printed | Color: Green | Sleeve: Full Sleeve | Neck: Round Neck | Occasion: Casual
    Description: Good quality sweatshirt for you.It gives you good comfort and a classy look.
[5] PID SWSFY382UZHFBCNB | Full Sleeve Printed Women Sweatshirt
    Brand: ECKO Unl | Price: ₹687 (was ₹2,149, 68% off) | Rating: 4.0/5 | in stock
    Fabric: Cotton Blend | Pattern: Printed | Color: Green | Sleeve: Full Sleeve | Neck: Hooded Neck | Occasion: Casual
[6] PID SWSFY36JNHCKZHZT | Full Sleeve Printed Men Sweatshirt
    Brand: ECKO Unl | Price: ₹719 (was ₹2,399, 70% off) | Rating: 2.5/5 | in stock
    Fabric: Cotton Blend | Pattern: Printed | Color: Multicolor | Sleeve: Full Sleeve | Neck: High Neck | Occasion: Casual
    Description: ECKO Unltd Solid French terry Regular Fit OLIVE/BLACK Sweat Shirt
[7] PID SWSFZEQEGPDK9GUB | Full Sleeve Printed Women Sweatshirt
    Brand: ECKO Unl | Price: ₹735 (was ₹2,299, 68% off) | Rating: 2.5/5 | in stock
    Fabric: Cotton Blend | Pattern: Printed | Color: Black | Sleeve: Full Sleeve | Neck: Hooded Neck | Occasion: Casual
    Description: ECKO Unltd Solid French terry Regular Fit BLACK Sweat Shirt
[8] PID SWSFY36HNVD3DUBF | Full Sleeve Printed Men Sweatshirt
    Brand: ECKO Unl | Price: ₹703 (was ₹2,199, 68% off) | Rating: 4.4/5 | in stock
    Fabric: Cotton Blend | Pattern: Printed | Color: Multicolor | Sleeve: Full Sleeve | Neck: Hooded Neck | Occasion: Casual
    Description: ECKO Unltd Solid French terry Regular Fit NAVY/TEAL/ORANGE Sweat Shirt

## Instructions
1. Check each product against the request: product type, gender, colour, material and any price or rating limit.
2. Pick the single best product. Prefer, in this order: matches the request, in stock, higher rating, better price.
3. Answer in this exact format, at most 120 words:
- Best Product: [PID] [title]
- Why: one or two sentences that cite the facts above (price, discount, rating, material, fit).
- Alternative: [PID] [title], and the trade-off compared with the best product (for example cheaper but lower rated). Leave out if none.
- Note: only if important information is missing (for example no rating listed).
4. Use only PIDs from the list above.
5. If no product matches the request, answer with exactly: "There are no good products that fit the request based on the retrieved results."

```
</details>

## `satin necktie set pocket square cufflinks`
*accessory set*

- Baseline retrieval (raw query): **20** products
- Improved retrieval (query `satin necktie set pocket square cufflinks`): **20** products, **8** shown to the LLM after de-duplication and constraints

**Baseline answer**

```
(dry run)
```

**Improved answer**

```
(dry run: LLM would be called with the prompt below)
```

<details><summary>What each LLM sees</summary>

Baseline context:
```
- PID: CTPFVZHY42MSZCF6, Title: nu-Lite Satin Tie & Cufflink  (Black)
- PID: CTPFVSTDBD7ZUHSB, Title: nu-Lite Satin Tie & Cufflink  (Multicolor)
- PID: CTPFVQZFE4HTFZNG, Title: nu-Lite Satin Tie & Cufflink  (Red)
- PID: CTPFVPZGUAYCWCKF, Title: nu-Lite Satin Tie & Cufflink  (Multicolor)
- PID: CTPFVPKJGJBXHQFJ, Title: nu-Lite Satin Tie & Cufflink  (Grey)
- PID: CTPFVZNX3KKES9DH, Title: nu-Lite Satin Tie & Cufflink  (Red)
- PID: CTPFVQZX4SZHHHHZ, Title: nu-Lite Satin Tie & Cufflink  (Beige)
- PID: CTPFVQP3GDSC3DUT, Title: nu-Lite Satin Tie & Cufflink  (Pink)
- PID: CTPFVQP2PEHKGYFQ, Title: nu-Lite Satin Tie & Cufflink  (Red)
- PID: CTPFVPZJKWRJ9A8H, Title: nu-Lite Satin Tie & Cufflink  (Multicolor)
- PID: CTPFVSSP8PNUTK2E, Title: nu-Lite Satin Tie & Cufflink  (Black)
- PID: CTPFVSTDYXRPXGKY, Title: nu-Lite Satin Tie & Cufflink  (Blue)
- PID: CTPFVQNHMEYKN3GA, Title: nu-Lite Satin Tie & Cufflink  (Black)
- PID: CTPFVUFZKYWWSW7M, Title: nu-Lite Satin Tie & Cufflink  (Yellow)
- PID: CTPFW63J86FZFHDS, Title: nu-Lite Satin Tie Pin Set  (Pink)
- PID: CTPFW6365D8JPGY5, Title: nu-Lite Satin Tie Pin Set  (Pink)
- PID: CTPFVPMTY2HZYSRR, Title: nu-Lite Satin Tie & Cufflink  (Black)
- PID: CTPFVPM3NDPBPPXE, Title: nu-Lite Satin Tie & Cufflink  (Purple)
- PID: CTPFVPHMVR9VQP2B, Title: nu-Lite Satin Tie & Cufflink  (Pink)
- PID: CTPFVPHGUPGV9SDK, Title: nu-Lite Satin Tie & Cufflink  (Brown)
```
Improved prompt:
```
## User request
satin necktie set pocket square cufflinks

## What the user asked for, read from the request
no price or rating limits

## Retrieved products (ranked by our search engine, best match first)
[1] PID CTPFVZHY42MSZCF6 | nu-Lite Satin Tie & Cufflink  (Black)
    Brand: not listed | Price: ₹499 (was ₹2,469, 79% off) | Rating: 2.7/5 | in stock
[2] PID CTPFVSTDBD7ZUHSB | nu-Lite Satin Tie & Cufflink  (Multicolor)
    Brand: not listed | Price: ₹499 (was ₹2,469, 79% off) | Rating: 2.7/5 | in stock
[3] PID CTPFVQZFE4HTFZNG | nu-Lite Satin Tie & Cufflink  (Red)
    Brand: not listed | Price: ₹499 (was ₹2,469, 79% off) | Rating: 2.7/5 | in stock
[4] PID CTPFVPKJGJBXHQFJ | nu-Lite Satin Tie & Cufflink  (Grey)
    Brand: not listed | Price: ₹499 (was ₹2,469, 79% off) | Rating: 2.7/5 | in stock
[5] PID CTPFVQZX4SZHHHHZ | nu-Lite Satin Tie & Cufflink  (Beige)
    Brand: not listed | Price: ₹499 (was ₹2,469, 79% off) | Rating: 4.0/5 | in stock
[6] PID CTPFVQP3GDSC3DUT | nu-Lite Satin Tie & Cufflink  (Pink)
    Brand: not listed | Price: ₹499 (was ₹2,469, 79% off) | Rating: 2.7/5 | in stock
[7] PID CTPFVSTDYXRPXGKY | nu-Lite Satin Tie & Cufflink  (Blue)
    Brand: not listed | Price: ₹699 (was ₹2,469, 71% off) | Rating: 2.7/5 | in stock
[8] PID CTPFVUFZKYWWSW7M | nu-Lite Satin Tie & Cufflink  (Yellow)
    Brand: not listed | Price: ₹599 (was ₹3,019, 80% off) | Rating: 2.7/5 | in stock

## Instructions
1. Check each product against the request: product type, gender, colour, material and any price or rating limit.
2. Pick the single best product. Prefer, in this order: matches the request, in stock, higher rating, better price.
3. Answer in this exact format, at most 120 words:
- Best Product: [PID] [title]
- Why: one or two sentences that cite the facts above (price, discount, rating, material, fit).
- Alternative: [PID] [title], and the trade-off compared with the best product (for example cheaper but lower rated). Leave out if none.
- Note: only if important information is missing (for example no rating listed).
4. Use only PIDs from the list above.
5. If no product matches the request, answer with exactly: "There are no good products that fit the request based on the retrieved results."

```
</details>

## `men slim jeans blue under 800`
*price limit written in the query*

- Baseline retrieval (raw query): **0** products
- Improved retrieval (query `men slim jeans blue`): **20** products, **4** shown to the LLM after de-duplication and constraints

**Baseline answer**

```
(dry run)
```

**Improved answer**

```
(dry run: LLM would be called with the prompt below)
```

<details><summary>What each LLM sees</summary>

Baseline context:
```
(empty)
```
Improved prompt:
```
## User request
men slim jeans blue under 800

## What the user asked for, read from the request
price between any and ₹800

## Retrieved products (ranked by our search engine, best match first)
[1] PID JEAFJM2P2FQQJF3C | Slim Men Dark Blue Jeans
    Brand: Absolu | Price: ₹589 (was ₹1,549, 61% off) | Rating: 4.1/5 | in stock
    Ideal For: Men | Fabric: Cotton Lycra Blend | Pattern: Solid | Color: Dark Blue | Closure: Button | Suitable For: Western Wear
    Description: Absolute High Quality Slim Fit Clean Look Navy Blue Jeans
[2] PID JEAEVJGUSXRNSHRY | Slim Men Dark Blue Jeans
    Brand: Absolu | Price: ₹489 (was ₹1,049, 53% off) | Rating: 3.8/5 | in stock
    Ideal For: Men | Fabric: Cotton Blend | Fit: Slim | Pattern: Solid | Color: Dark Blue | Closure: Button
    Description: Absolute High quality Smart-fit Dark Blue Jeans For Men's
[3] PID JEAFDWG9K7KPKHS8 | Slim Men Blue Jeans
    Brand: NEBRAS | Price: ₹599 (was ₹1,499, 60% off) | Rating: 4.1/5 | in stock
    Ideal For: Men | Fabric: Cotton Lycra Blend | Pattern: Washed | Color: Blue | Closure: Buttoned | Suitable For: Western Wear
    Description: Authentic Mens Slim Fit Jean. This jean is constructed with durable materials built for long-lasting comfort. These jeans sit below the waist with a slim fit from hip to ankle....
[4] PID JEAFDHHGY3HBXEMP | Stretchable Regular Men Blue Jeans
    Brand: NEBRAS | Price: ₹629 (was ₹1,499, 58% off) | Rating: 3.6/5 | in stock
    Ideal For: Men | Fabric: Cotton Lycra Blend | Pattern: Acid Washed | Color: Blue | Closure: Button | Suitable For: Western Wear
    Description: Authentic Mens Slim Fit Jean. This jean is constructed with durable materials built for long-lasting comfort. These jeans sit below the waist with a slim fit from hip to ankle....

## Instructions
1. Check each product against the request: product type, gender, colour, material and any price or rating limit.
2. Pick the single best product. Prefer, in this order: matches the request, in stock, higher rating, better price.
3. Answer in this exact format, at most 120 words:
- Best Product: [PID] [title]
- Why: one or two sentences that cite the facts above (price, discount, rating, material, fit).
- Alternative: [PID] [title], and the trade-off compared with the best product (for example cheaper but lower rated). Leave out if none.
- Note: only if important information is missing (for example no rating listed).
4. Use only PIDs from the list above.
5. If no product matches the request, answer with exactly: "There are no good products that fit the request based on the retrieved results."

```
</details>

## `cheap men solid blue track pants`
*soft preference: low price*

- Baseline retrieval (raw query): **0** products
- Improved retrieval (query `men solid blue track pants`): **20** products, **8** shown to the LLM after de-duplication and constraints

**Baseline answer**

```
(dry run)
```

**Improved answer**

```
(dry run: LLM would be called with the prompt below)
```

<details><summary>What each LLM sees</summary>

Baseline context:
```
(empty)
```
Improved prompt:
```
## User request
cheap men solid blue track pants

## What the user asked for, read from the request
prefers a low price

## Retrieved products (ranked by our search engine, best match first)
[1] PID TKPFWJKKUNUJHH9P | Solid Men Blue Track Pants
    Brand: REAZ | Price: ₹361 (was ₹1,199, 69% off) | Rating: 4.3/5 | in stock
    Fabric: Pure Cotton | Pattern: Solid | Color: Blue | Closure: Elastic, Drawstring
[2] PID TKPFYKZZ58DPUZ6N | Solid Men Blue Track Pants
    Brand: REAZ | Price: ₹370 (was ₹1,199, 69% off) | Rating: 3.7/5 | in stock
    Fabric: Pure Cotton | Pattern: Solid | Color: Blue | Closure: Drawstring
[3] PID TKPFYVRNV6MHFGZA | Solid Men Blue Track Pants
    Brand: MASH UNLIMIT | Price: ₹399 (was ₹999, 60% off) | Rating: 3.2/5 | in stock
    Fabric: Cotton Blend | Pattern: Solid | Color: Blue
    Description: Mash Unlimited Men'S Navy Side Tape Casual Track Pant
[4] PID TKPFTE9AHFFFMBYE | Solid Men Blue Track Pants
    Brand: JACK AND HAR | Price: ₹399 (was ₹1,499, 73% off) | Rating: 3.4/5 | in stock
    Fabric: Polyester | Pattern: Solid | Color: Blue | Closure: Elastic
    Description: ts range of super comfortable and trendy track pants. The track pants are made out of very fine fabric. The colored rib on waist and bottoms adds to the fashionable look. Wear...
[5] PID TKPFKS96T88SUYBZ | Solid Men Blue Track Pants
    Brand: T10 Spor | Price: ₹499 (was ₹999, 50% off) | Rating: 2.3/5 | in stock
    Fabric: Cotton Silk | Pattern: Solid | Color: Blue
[6] PID TKPFPG2HJBBWFDAR | Solid Men Blue Track Pants
    Brand: LIVST | Price: ₹519 (was ₹899, 42% off) | Rating: 3.3/5 | in stock
    Fabric: Polyester | Pattern: Solid | Color: Blue
[7] PID TKPF3FPZRRJUWTAZ | Solid Men Blue, Black Track Pants
    Brand: Fairdea | Price: ₹538 (was ₹1,299, 58% off) | Rating: 2.6/5 | in stock
    Fabric: Polycotton | Pattern: Solid | Color: Blue, Black | Closure: Elastic
    Description: Look urban and feel relaxed by slipping into these track pants for men from Direction of Desire. Made from a polyester blend, these track pants are really comfortable to wear....
[8] PID TKPFRR83HDEPCQD6 | Solid Men Blue Track Pants
    Brand: ECKO Unl | Price: ₹559 (was ₹799, 30% off) | Rating: 3.6/5 | in stock
    Fabric: Cotton Blend | Pattern: Solid | Color: Blue

## Instructions
1. Check each product against the request: product type, gender, colour, material and any price or rating limit.
2. Pick the single best product. Prefer, in this order: matches the request, in stock, higher rating, better price.
3. Answer in this exact format, at most 120 words:
- Best Product: [PID] [title]
- Why: one or two sentences that cite the facts above (price, discount, rating, material, fit).
- Alternative: [PID] [title], and the trade-off compared with the best product (for example cheaper but lower rated). Leave out if none.
- Note: only if important information is missing (for example no rating listed).
4. Use only PIDs from the list above.
5. If no product matches the request, answer with exactly: "There are no good products that fit the request based on the retrieved results."

```
</details>

## `women sweatshirt rating above 4`
*rating limit written in the query*

- Baseline retrieval (raw query): **0** products
- Improved retrieval (query `women sweatshirt`): **20** products, **7** shown to the LLM after de-duplication and constraints

**Baseline answer**

```
(dry run)
```

**Improved answer**

```
(dry run: LLM would be called with the prompt below)
```

<details><summary>What each LLM sees</summary>

Baseline context:
```
(empty)
```
Improved prompt:
```
## User request
women sweatshirt rating above 4

## What the user asked for, read from the request
rating of at least 4.0/5

## Retrieved products (ranked by our search engine, best match first)
[1] PID SWSFMTNHE2PCYWFZ | Full Sleeve Solid Women Sweatshirt
    Brand: ARBO | Price: ₹854 (was ₹1,900, 55% off) | Rating: 4.2/5 | in stock
    Fabric: Polycotton | Pattern: Solid | Color: Blue | Sleeve: Full Sleeve | Neck: Collared Neck | Occasion: Casual
    Description: Arbour gives you the new trends Sweatshirt for women’s. Arbour provides all the size variants in the Sweatshirt. Sweatshirt is made by Polycotton and all the Sweatshirt are...
[2] PID SWSFMF3AVA9FPFDJ | Full Sleeve Solid Women Sweatshirt
    Brand: ARBO | Price: ₹835 (was ₹1,660, 49% off) | Rating: 4.2/5 | in stock
    Fabric: Polycotton | Pattern: Solid | Color: Grey | Sleeve: Full Sleeve | Neck: Mandarin Collar | Occasion: Casual
    Description: Arbour gives you the new trends sweatshirt for women’s. Arbour provides all the size variants in the sweatshirt. sweatshirt is made by Polycotton and all the sweatshirt are...
[3] PID SWSFMF3AUHYGMGYF | Full Sleeve Solid Women Sweatshirt
    Brand: ARBO | Price: ₹930 (was ₹1,860, 50% off) | Rating: 4.2/5 | in stock
    Fabric: Polycotton | Pattern: Solid | Color: Blue | Sleeve: Full Sleeve | Neck: Mandarin Collar | Occasion: Casual
    Description: Arbour gives you the new trends sweatshirt for women’s. Arbour provides all the size variants in the sweatshirt. sweatshirt is made by Polycotton and all the sweatshirt are...
[4] PID SWSFMJGTVFW3NAXZ | Full Sleeve Solid Women Sweatshirt
    Brand: ARBO | Price: ₹759 (was ₹1,900, 60% off) | Rating: 4.2/5 | in stock
    Fabric: Polycotton | Pattern: Solid | Color: Black | Sleeve: Full Sleeve | Neck: Hooded Neck | Occasion: Casual
    Description: Arbour gives you the new trends Sweatshirt for women’s. Arbour provides all the size variants in the Sweatshirt. Sweatshirt is made by Polycotton and all the Sweatshirt are...
[5] PID SWSFMJGTGZMJXK5H | Full Sleeve Solid Women Sweatshirt
    Brand: ARBO | Price: ₹949 (was ₹1,998, 52% off) | Rating: 4.2/5 | in stock
    Fabric: Polycotton | Pattern: Solid | Color: Black | Sleeve: Full Sleeve | Neck: Hooded Neck | Occasion: Casual
    Description: Arbour gives you the new trends Sweatshirt for women’s. Arbour provides all the size variants in the Sweatshirt. Sweatshirt is made by Polycotton and all the Sweatshirt are...
[6] PID SWSFMKGBF7FWZ3Q4 | Full Sleeve Solid Women Sweatshirt
    Brand: ARBO | Price: ₹635 (was ₹799, 20% off) | Rating: 4.2/5 | in stock
    Fabric: Polycotton | Pattern: Solid | Color: Black | Sleeve: Full Sleeve | Neck: Hooded Neck | Occasion: Casual
    Description: Arbour gives you the new trends Sweatshirt for women’s. Arbour provides all the size variants in the Sweatshirt. Sweatshirt is made by Polycotton and all the Sweatshirt are...
[7] PID SWSFNV7N26KC54MB | Full Sleeve Solid Women Sweatshirt
    Brand: ARBO | Price: ₹407 (was ₹740, 45% off) | Rating: 4.3/5 | in stock
    Fabric: Cotton Blend | Pattern: Solid | Color: Beige | Sleeve: Full Sleeve | Neck: V Neck | Suitable For: Western Wear
    Description: You will always be the center of attraction of any gathering by this sweatshirt.

## Instructions
1. Check each product against the request: product type, gender, colour, material and any price or rating limit.
2. Pick the single best product. Prefer, in this order: matches the request, in stock, higher rating, better price.
3. Answer in this exact format, at most 120 words:
- Best Product: [PID] [title]
- Why: one or two sentences that cite the facts above (price, discount, rating, material, fit).
- Alternative: [PID] [title], and the trade-off compared with the best product (for example cheaper but lower rated). Leave out if none.
- Note: only if important information is missing (for example no rating listed).
4. Use only PIDs from the list above.
5. If no product matches the request, answer with exactly: "There are no good products that fit the request based on the retrieved results."

```
</details>

## `men formal shirt under 200`
*price limit that no product meets*

- Baseline retrieval (raw query): **1** products
- Improved retrieval (query `men formal shirt`): **20** products, **0** shown to the LLM after de-duplication and constraints

**Baseline answer**

```
(dry run)
```

**Improved answer**

```
There are no good products that fit the request based on the retrieved results. (the cheapest retrieved product costs ₹499, above your limit of ₹200.)
```

<details><summary>What each LLM sees</summary>

Baseline context:
```
- PID: FABFZPXQ2ZT2MR47, Title: Rayon Printed Shirt Fabric  (Unstitched)
```
Improved prompt:
```
(no LLM call: answered by the gate)
```
</details>

## `waterproof hiking boots`
*nothing in the catalogue matches*

- Baseline retrieval (raw query): **0** products
- Improved retrieval (query `waterproof hiking boots`): **0** products, **0** shown to the LLM after de-duplication and constraints

**Baseline answer**

```
(dry run)
```

**Improved answer**

```
No products matched every word of your search. Try fewer or more general words (for example drop the colour or the brand).
```

<details><summary>What each LLM sees</summary>

Baseline context:
```
(empty)
```
Improved prompt:
```
(no LLM call: answered by the gate)
```
</details>
