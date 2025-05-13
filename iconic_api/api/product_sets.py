from typing import Optional, List, Dict, Any, Union, TypeVar, Generic

from .base_api_module import BaseAPIModule
from ..models import (
    ProductSetRead,
    ProductSetCreated,
    ListProductSetsRequest,
    CreateProductSetRequest,
    UpdateProductSetRequest,
    AddProductSetImageRequest,
    GetCountByAttributeSetRequest,
    UpdateProductSetImageRequest,
    ProductSetIdsRequest,
    GetQualityControlStatusRequest,
    GetImagesBySKURequest,
    QualityControlStatus,
    ProductImageBySKU,
    Image,
    ProductSetsImage,
    ProductSetsCoverImage,
    ProductSetsTag,
    Product,
    ProductRead,
    HybridProduct,
    CreateProductRequest,
    UpdateProductRequest,
    SearchHybridRequest,
    CreateProductBySinRequest,
    ProductGroupRequest,
    PriceRead,
    UpdateProductSetPriceRequest
)

T = TypeVar('T')

class PaginatedResponse(Generic[T]):
    """Generic class for paginated responses."""
    def __init__(self, items: List[T], limit: int, offset: int, total_count: int):
        self.items = items
        self.limit = limit
        self.offset = offset
        self.total_count = total_count

class ProductSetsAPI(BaseAPIModule):
    def list_product_sets(self, params: ListProductSetsRequest) -> PaginatedResponse[ProductSetRead]:
        """
        Get list of ProductSets based on filter criteria.
        
        Args:
            params: Filter and pagination parameters
            
        Returns:
            A paginated response containing product sets
        """
        response_data = self._client._make_request_sync("GET", "/v2/product-sets", params=params.to_api_params())
        
        # Extract pagination data and create items list
        items = [ProductSetRead(**item) for item in response_data.get("items", [])]
        pagination = response_data.get("pagination", {})
        limit = pagination.get("limit", params.limit)
        offset = pagination.get("offset", params.offset)
        total_count = pagination.get("totalCount", len(items))
        
        return PaginatedResponse(items, limit, offset, total_count)

    async def list_product_sets_async(self, params: ListProductSetsRequest) -> PaginatedResponse[ProductSetRead]:
        """
        Get list of ProductSets based on filter criteria (async).
        
        Args:
            params: Filter and pagination parameters
            
        Returns:
            A paginated response containing product sets
        """
        response_data = await self._client._make_request_async("GET", "/v2/product-sets", params=params.to_api_params())
        
        # Extract pagination data and create items list
        items = [ProductSetRead(**item) for item in response_data.get("items", [])]
        pagination = response_data.get("pagination", {})
        limit = pagination.get("limit", params.limit)
        offset = pagination.get("offset", params.offset)
        total_count = pagination.get("totalCount", len(items))
        
        return PaginatedResponse(items, limit, offset, total_count)

    def create_product_set(self, payload: CreateProductSetRequest) -> ProductSetCreated:
        """
        Create a new product set with a single product/variation.
        
        Args:
            payload: The product set data to create
            
        Returns:
            The newly created product set
        """
        # Convert the payload to camelCase for API
        prepared_payload = self._prepare_payload(payload.model_dump(by_alias=True, exclude_none=True))
        
        response_data = self._client._make_request_sync(
            "POST", 
            "/v2/product-set", 
            json_data=prepared_payload
        )
        
        return ProductSetCreated(**response_data)

    async def create_product_set_async(self, payload: CreateProductSetRequest) -> ProductSetCreated:
        """
        Create a new product set with a single product/variation (async).
        
        Args:
            payload: The product set data to create
            
        Returns:
            The newly created product set
        """
        # Convert the payload to camelCase for API
        prepared_payload = self._prepare_payload(payload.model_dump(by_alias=True, exclude_none=True))
        
        response_data = await self._client._make_request_async(
            "POST", 
            "/v2/product-set", 
            json_data=prepared_payload
        )
        
        return ProductSetCreated(**response_data)
        
    def get_product_set(self, product_set_id: int) -> ProductSetRead:
        """
        Get ProductSet entity by Id.
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            
        Returns:
            The requested product set
        """
        response_data = self._client._make_request_sync(
            "GET", 
            f"/v2/product-set/{product_set_id}" 
        )
        
        return ProductSetRead(**response_data)
    
    async def get_product_set_async(self, product_set_id: int) -> ProductSetRead:
        """
        Get ProductSet entity by Id (async).
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            
        Returns:
            The requested product set
        """
        response_data = await self._client._make_request_async(
            "GET", 
            f"/v2/product-set/{product_set_id}" 
        )
        
        return ProductSetRead(**response_data)
    
    def update_product_set(self, product_set_id: int, payload: UpdateProductSetRequest) -> ProductSetRead:
        """
        Update Product Set level attributes.
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            payload: The updated product set data
            
        Returns:
            The updated product set
        """
        prepared_payload = self._prepare_payload(payload.model_dump(by_alias=True, exclude_none=True))
        
        response_data = self._client._make_request_sync(
            "PUT", 
            f"/v2/product-set/{product_set_id}", 
            json_data=prepared_payload
        )
        
        return ProductSetRead(**response_data)
    
    async def update_product_set_async(self, product_set_id: int, payload: UpdateProductSetRequest) -> ProductSetRead:
        """
        Update Product Set level attributes (async).
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            payload: The updated product set data
            
        Returns:
            The updated product set
        """
        prepared_payload = self._prepare_payload(payload.model_dump(by_alias=True, exclude_none=True))
        
        response_data = await self._client._make_request_async(
            "PUT", 
            f"/v2/product-set/{product_set_id}", 
            json_data=prepared_payload
        )
        
        return ProductSetRead(**response_data)
    
    def get_product_set_by_parent_sku(self, parent_sku: str) -> ProductSetRead:
        """
        Get single ProductSet with parent sku.
        
        Args:
            parent_sku: ParentSku of ProductSet
            
        Returns:
            The requested product set
        """
        response_data = self._client._make_request_sync(
            "GET", 
            f"/v2/product-set/parent-sku/{parent_sku}" 
        )
        
        return ProductSetRead(**response_data)
    
    async def get_product_set_by_parent_sku_async(self, parent_sku: str) -> ProductSetRead:
        """
        Get single ProductSet with parent sku (async).
        
        Args:
            parent_sku: ParentSku of ProductSet
            
        Returns:
            The requested product set
        """
        response_data = await self._client._make_request_async(
            "GET", 
            f"/v2/product-set/parent-sku/{parent_sku}" 
        )
        
        return ProductSetRead(**response_data)
    
    def get_product_set_by_config_sku(self, config_sku: str) -> ProductSetRead:
        """
        Get ProductSet by its ConfigSku.
        
        Args:
            config_sku: String ConfigSku of ProductSet
            
        Returns:
            The requested product set
        """
        response_data = self._client._make_request_sync(
            "GET", 
            f"/v2/product-set/config-sku/{config_sku}" 
        )
        
        return ProductSetRead(**response_data)
    
    async def get_product_set_by_config_sku_async(self, config_sku: str) -> ProductSetRead:
        """
        Get ProductSet by its ConfigSku (async).
        
        Args:
            config_sku: String ConfigSku of ProductSet
            
        Returns:
            The requested product set
        """
        response_data = await self._client._make_request_async(
            "GET", 
            f"/v2/product-set/config-sku/{config_sku}" 
        )
        
        return ProductSetRead(**response_data)
    
    def get_count_by_attribute_set(self, params: GetCountByAttributeSetRequest) -> List[Dict[str, Any]]:
        """
        Get count of ProductSets grouped by AttributeSet.
        
        Args:
            params: Filter parameters
            
        Returns:
            List of attribute set IDs with counts
        """
        response_data = self._client._make_request_sync(
            "GET", 
            "/v2/product-set/count-by-attribute-set", 
            params=params.to_api_params()
        )
        
        return response_data
    
    async def get_count_by_attribute_set_async(self, params: GetCountByAttributeSetRequest) -> List[Dict[str, Any]]:
        """
        Get count of ProductSets grouped by AttributeSet (async).
        
        Args:
            params: Filter parameters
            
        Returns:
            List of attribute set IDs with counts
        """
        response_data = await self._client._make_request_async(
            "GET", 
            "/v2/product-set/count-by-attribute-set", 
            params=params.to_api_params()
        )
        
        return response_data
    
    def get_product_set_images(self, product_set_id: int) -> List[Image]:
        """
        Get a list of the product-set's images.
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            
        Returns:
            List of product set images
        """
        response_data = self._client._make_request_sync(
            "GET", 
            f"/v2/product-set/{product_set_id}/images" 
        )
        
        return [Image(**item) for item in response_data]
    
    async def get_product_set_images_async(self, product_set_id: int) -> List[Image]:
        """
        Get a list of the product-set's images (async).
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            
        Returns:
            List of product set images
        """
        response_data = await self._client._make_request_async(
            "GET", 
            f"/v2/product-set/{product_set_id}/images" 
        )
        
        return [Image(**item) for item in response_data]
    
    def add_product_set_image(self, product_set_id: int, payload: AddProductSetImageRequest) -> Image:
        """
        Add an image to the product-set using a URL.
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            payload: Image data including URL and optional position
            
        Returns:
            The added image
        """
        prepared_payload = self._prepare_payload(payload.model_dump(by_alias=True, exclude_none=True))
        
        response_data = self._client._make_request_sync(
            "POST", 
            f"/v2/product-set/{product_set_id}/images", 
            json_data=prepared_payload
        )
        
        return Image(**response_data)
    
    async def add_product_set_image_async(self, product_set_id: int, payload: AddProductSetImageRequest) -> Image:
        """
        Add an image to the product-set using a URL (async).
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            payload: Image data including URL and optional position
            
        Returns:
            The added image
        """
        prepared_payload = self._prepare_payload(payload.model_dump(by_alias=True, exclude_none=True))
        
        response_data = await self._client._make_request_async(
            "POST", 
            f"/v2/product-set/{product_set_id}/images", 
            json_data=prepared_payload
        )
        
        return Image(**response_data)
    
    def upload_product_set_image(self, product_set_id: int, image_file_path: str, position: Optional[int] = None, overwrite: bool = False) -> Image:
        """
        Add an image to the product-set by uploading a file.
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            image_file_path: Path to the image file to upload
            position: Optional position for the image
            overwrite: Whether to overwrite an existing image at the position
            
        Returns:
            The added image
        """
        with open(image_file_path, "rb") as f:
            files = {"file1": (image_file_path.split('/')[-1], f)}
            form_data = {}
            
            if position is not None:
                form_data["position"] = str(position)
                
            if overwrite:
                form_data["overwrite"] = "true"
            
            response_data = self._client._make_request_sync(
                "POST", 
                f"/v2/product-set/{product_set_id}/images", 
                form_data=form_data,
                files=files
            )
        
        return Image(**response_data)
    
    async def upload_product_set_image_async(self, product_set_id: int, image_file_path: str, position: Optional[int] = None, overwrite: bool = False) -> Image:
        """
        Add an image to the product-set by uploading a file (async).
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            image_file_path: Path to the image file to upload
            position: Optional position for the image
            overwrite: Whether to overwrite an existing image at the position
            
        Returns:
            The added image
        """
        with open(image_file_path, "rb") as f:
            files = {"file1": (image_file_path.split('/')[-1], f)}
            form_data = {}
            
            if position is not None:
                form_data["position"] = str(position)
                
            if overwrite:
                form_data["overwrite"] = "true"
            
            response_data = await self._client._make_request_async(
                "POST", 
                f"/v2/product-set/{product_set_id}/images", 
                form_data=form_data,
                files=files
            )
        
        return Image(**response_data)
    
    def update_product_set_image(self, product_set_id: int, image_id: int, payload: UpdateProductSetImageRequest) -> Image:
        """
        Update an image of the product-set using a URL.
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            image_id: Numeric ID of the Image
            payload: Image data including URL and/or position
            
        Returns:
            The updated image
        """
        prepared_payload = self._prepare_payload(payload.model_dump(by_alias=True, exclude_none=True))
        
        response_data = self._client._make_request_sync(
            "PATCH", 
            f"/v2/product-set/{product_set_id}/images/{image_id}", 
            json_data=prepared_payload
        )
        
        return Image(**response_data)
    
    async def update_product_set_image_async(self, product_set_id: int, image_id: int, payload: UpdateProductSetImageRequest) -> Image:
        """
        Update an image of the product-set using a URL (async).
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            image_id: Numeric ID of the Image
            payload: Image data including URL and/or position
            
        Returns:
            The updated image
        """
        prepared_payload = self._prepare_payload(payload.model_dump(by_alias=True, exclude_none=True))
        
        response_data = await self._client._make_request_async(
            "PATCH", 
            f"/v2/product-set/{product_set_id}/images/{image_id}", 
            json_data=prepared_payload
        )
        
        return Image(**response_data)
    
    def upload_updated_product_set_image(self, product_set_id: int, image_id: int, image_file_path: str, position: Optional[int] = None) -> Image:
        """
        Update an image of the product-set by uploading a new file.
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            image_id: Numeric ID of the Image
            image_file_path: Path to the image file to upload
            position: Optional position for the image
            
        Returns:
            The updated image
        """
        with open(image_file_path, "rb") as f:
            files = {"file1": (image_file_path.split('/')[-1], f)}
            form_data = {}
            
            if position is not None:
                form_data["position"] = str(position)
            
            response_data = self._client._make_request_sync(
                "PATCH", 
                f"/v2/product-set/{product_set_id}/images/{image_id}", 
                form_data=form_data,
                files=files
            )
        
        return Image(**response_data)
    
    async def upload_updated_product_set_image_async(self, product_set_id: int, image_id: int, image_file_path: str, position: Optional[int] = None) -> Image:
        """
        Update an image of the product-set by uploading a new file (async).
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            image_id: Numeric ID of the Image
            image_file_path: Path to the image file to upload
            position: Optional position for the image
            
        Returns:
            The updated image
        """
        with open(image_file_path, "rb") as f:
            files = {"file1": (image_file_path.split('/')[-1], f)}
            form_data = {}
            
            if position is not None:
                form_data["position"] = str(position)
            
            response_data = await self._client._make_request_async(
                "PATCH", 
                f"/v2/product-set/{product_set_id}/images/{image_id}", 
                form_data=form_data,
                files=files
            )
        
        return Image(**response_data)
        
    def delete_product_set_image(self, product_set_id: int, image_id: int) -> None:
        """
        Delete an image of the product-set.
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            image_id: Numeric ID of the Image
        """
        self._client._make_request_sync(
            "DELETE", 
            f"/v2/product-set/{product_set_id}/images/{image_id}"
        )
    
    async def delete_product_set_image_async(self, product_set_id: int, image_id: int) -> None:
        """
        Delete an image of the product-set (async).
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            image_id: Numeric ID of the Image
        """
        await self._client._make_request_async(
            "DELETE", 
            f"/v2/product-set/{product_set_id}/images/{image_id}"
        )
        
    def get_products(self, product_set_id: int) -> List[ProductRead]:
        """
        Get list of products for a ProductSet.
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            
        Returns:
            List of products in the product set
        """
        response_data = self._client._make_request_sync(
            "GET", 
            f"/v2/product-set/{product_set_id}/products"
        )
        
        return [ProductRead(**item) for item in response_data]
    
    async def get_products_async(self, product_set_id: int) -> List[ProductRead]:
        """
        Get list of products for a ProductSet (async).
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            
        Returns:
            List of products in the product set
        """
        response_data = await self._client._make_request_async(
            "GET", 
            f"/v2/product-set/{product_set_id}/products"
        )
        
        return [ProductRead(**item) for item in response_data]
    
    def create_product(self, product_set_id: int, payload: CreateProductRequest) -> ProductRead:
        """
        Creates a new product for a product set.
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            payload: The product data to create
            
        Returns:
            The newly created product
        """
        prepared_payload = self._prepare_payload(payload.model_dump(exclude_none=True))
        
        response_data = self._client._make_request_sync(
            "POST", 
            f"/v2/product-set/{product_set_id}/products", 
            json_data=prepared_payload
        )
        
        return ProductRead(**response_data)
    
    async def create_product_async(self, product_set_id: int, payload: CreateProductRequest) -> ProductRead:
        """
        Creates a new product for a product set (async).
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            payload: The product data to create
            
        Returns:
            The newly created product
        """
        prepared_payload = self._prepare_payload(payload.model_dump(exclude_none=True))
        
        response_data = await self._client._make_request_async(
            "POST", 
            f"/v2/product-set/{product_set_id}/products", 
            json_data=prepared_payload
        )
        
        return ProductRead(**response_data)
        
    def search_hybrid(self, params: SearchHybridRequest) -> List[HybridProduct]:
        """
        Search results of Hybrid Products from Shop.
        
        Args:
            params: Search query parameters
            
        Returns:
            List of hybrid products matching the search query
        """
        response_data = self._client._make_request_sync(
            "GET", 
            "/v2/product-set/search-hybrid", 
            params=params.to_api_params()
        )
        
        return [HybridProduct(**item) for item in response_data]
    
    async def search_hybrid_async(self, params: SearchHybridRequest) -> List[HybridProduct]:
        """
        Search results of Hybrid Products from Shop (async).
        
        Args:
            params: Search query parameters
            
        Returns:
            List of hybrid products matching the search query
        """
        response_data = await self._client._make_request_async(
            "GET", 
            "/v2/product-set/search-hybrid", 
            params=params.to_api_params()
        )
        
        return [HybridProduct(**item) for item in response_data]
    
    def create_product_by_sin(self, payload: CreateProductBySinRequest) -> Dict[str, int]:
        """
        Create Products by SIN in Shop's catalog.
        
        Args:
            payload: The SIN data to use for product creation
            
        Returns:
            Dictionary with the ID of the created product set
        """
        prepared_payload = self._prepare_payload(payload.model_dump(exclude_none=True))
        
        response_data = self._client._make_request_sync(
            "POST", 
            "/v2/product-set/products/create-by-sin", 
            json_data=prepared_payload
        )
        
        return response_data
    
    async def create_product_by_sin_async(self, payload: CreateProductBySinRequest) -> Dict[str, int]:
        """
        Create Products by SIN in Shop's catalog (async).
        
        Args:
            payload: The SIN data to use for product creation
            
        Returns:
            Dictionary with the ID of the created product set
        """
        prepared_payload = self._prepare_payload(payload.model_dump(exclude_none=True))
        
        response_data = await self._client._make_request_async(
            "POST", 
            "/v2/product-set/products/create-by-sin", 
            json_data=prepared_payload
        )
        
        return response_data
        
    def update_product_status(self, product_set_id: int, product_id: int, status: str) -> None:
        """
        Update Product status.
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            product_id: Numeric ID of the Product
            status: New status for the product (active, inactive, deleted)
        """
        params = {"status": status}
        
        self._client._make_request_sync(
            "PUT", 
            f"/v2/product-set/{product_set_id}/products/{product_id}/status", 
            params=params
        )
    
    async def update_product_status_async(self, product_set_id: int, product_id: int, status: str) -> None:
        """
        Update Product status (async).
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            product_id: Numeric ID of the Product
            status: New status for the product (active, inactive, deleted)
        """
        params = {"status": status}
        
        await self._client._make_request_async(
            "PUT", 
            f"/v2/product-set/{product_set_id}/products/{product_id}/status", 
            params=params
        )
        
    def get_product(self, product_set_id: int, product_id: int) -> ProductRead:
        """
        Get product by ID.
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            product_id: Numeric ID of the Product
            
        Returns:
            The requested product
        """
        response_data = self._client._make_request_sync(
            "GET", 
            f"/v2/product-set/{product_set_id}/products/{product_id}"
        )
        
        return ProductRead(**response_data)
    
    async def get_product_async(self, product_set_id: int, product_id: int) -> ProductRead:
        """
        Get product by ID (async).
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            product_id: Numeric ID of the Product
            
        Returns:
            The requested product
        """
        response_data = await self._client._make_request_async(
            "GET", 
            f"/v2/product-set/{product_set_id}/products/{product_id}"
        )
        
        return ProductRead(**response_data)
    
    def update_product(self, product_set_id: int, product_id: int, payload: UpdateProductRequest) -> ProductRead:
        """
        Update Product.
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            product_id: Numeric ID of the Product
            payload: The updated product data
            
        Returns:
            The updated product
        """
        prepared_payload = self._prepare_payload(payload.model_dump(exclude_none=True))
        
        response_data = self._client._make_request_sync(
            "PUT", 
            f"/v2/product-set/{product_set_id}/products/{product_id}", 
            json_data=prepared_payload
        )
        
        return ProductRead(**response_data)
    
    async def update_product_async(self, product_set_id: int, product_id: int, payload: UpdateProductRequest) -> ProductRead:
        """
        Update Product (async).
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            product_id: Numeric ID of the Product
            payload: The updated product data
            
        Returns:
            The updated product
        """
        prepared_payload = self._prepare_payload(payload.model_dump(exclude_none=True))
        
        response_data = await self._client._make_request_async(
            "PUT", 
            f"/v2/product-set/{product_set_id}/products/{product_id}", 
            json_data=prepared_payload
        )
        
        return ProductRead(**response_data)
        
    def get_product_group(self, product_set_id: int) -> Dict[str, str]:
        """
        Get group name of the product set.
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            
        Returns:
            Dictionary with the group name
        """
        response_data = self._client._make_request_sync(
            "GET", 
            f"/v2/product-set/{product_set_id}/group"
        )
        
        return response_data
    
    async def get_product_group_async(self, product_set_id: int) -> Dict[str, str]:
        """
        Get group name of the product set (async).
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            
        Returns:
            Dictionary with the group name
        """
        response_data = await self._client._make_request_async(
            "GET", 
            f"/v2/product-set/{product_set_id}/group"
        )
        
        return response_data
    
    def add_to_product_group(self, product_set_id: int, payload: ProductGroupRequest) -> Dict[str, str]:
        """
        Add product to group.
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            payload: The group data
            
        Returns:
            Dictionary with the group name
        """
        prepared_payload = self._prepare_payload(payload.model_dump(exclude_none=True))
        
        response_data = self._client._make_request_sync(
            "POST", 
            f"/v2/product-set/{product_set_id}/group", 
            json_data=prepared_payload
        )
        
        return response_data
    
    async def add_to_product_group_async(self, product_set_id: int, payload: ProductGroupRequest) -> Dict[str, str]:
        """
        Add product to group (async).
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            payload: The group data
            
        Returns:
            Dictionary with the group name
        """
        prepared_payload = self._prepare_payload(payload.model_dump(exclude_none=True))
        
        response_data = await self._client._make_request_async(
            "POST", 
            f"/v2/product-set/{product_set_id}/group", 
            json_data=prepared_payload
        )
        
        return response_data
    
    def remove_from_product_group(self, product_set_id: int) -> None:
        """
        Remove product set from group.
        
        Args:
            product_set_id: Numeric ID of the ProductSet
        """
        self._client._make_request_sync(
            "DELETE", 
            f"/v2/product-set/{product_set_id}/group"
        )
    
    async def remove_from_product_group_async(self, product_set_id: int) -> None:
        """
        Remove product set from group (async).
        
        Args:
            product_set_id: Numeric ID of the ProductSet
        """
        await self._client._make_request_async(
            "DELETE", 
            f"/v2/product-set/{product_set_id}/group"
        )
    
    def get_product_sets_cover_images(self, product_set_ids: List[int]) -> List[ProductSetsCoverImage]:
        """
        Get the URL of main images by product sets ids.
        
        Args:
            product_set_ids: List of ProductSet ids (max 100)
            
        Returns:
            List of product set cover images
        """
        params = {"productSetIds[]": product_set_ids}
        
        response_data = self._client._make_request_sync(
            "GET", 
            "/v2/product-sets/cover-image", 
            params=params
        )
        
        return [ProductSetsCoverImage(**item) for item in response_data]
    
    async def get_product_sets_cover_images_async(self, product_set_ids: List[int]) -> List[ProductSetsCoverImage]:
        """
        Get the URL of main images by product sets ids (async).
        
        Args:
            product_set_ids: List of ProductSet ids (max 100)
            
        Returns:
            List of product set cover images
        """
        params = {"productSetIds[]": product_set_ids}
        
        response_data = await self._client._make_request_async(
            "GET", 
            "/v2/product-sets/cover-image", 
            params=params
        )
        
        return [ProductSetsCoverImage(**item) for item in response_data]
    
    def get_product_sets_images(self, product_set_ids: List[int]) -> List[ProductSetsImage]:
        """
        Get the images by product sets ids.
        
        Args:
            product_set_ids: List of ProductSet ids (max 100)
            
        Returns:
            List of product sets with their images
        """
        params = {"productSetIds[]": product_set_ids}
        
        response_data = self._client._make_request_sync(
            "GET", 
            "/v2/product-sets/images", 
            params=params
        )
        
        return [ProductSetsImage(**item) for item in response_data]
    
    async def get_product_sets_images_async(self, product_set_ids: List[int]) -> List[ProductSetsImage]:
        """
        Get the images by product sets ids (async).
        
        Args:
            product_set_ids: List of ProductSet ids (max 100)
            
        Returns:
            List of product sets with their images
        """
        params = {"productSetIds[]": product_set_ids}
        
        response_data = await self._client._make_request_async(
            "GET", 
            "/v2/product-sets/images", 
            params=params
        )
        
        return [ProductSetsImage(**item) for item in response_data]
    
    def get_product_sets_tags(self, product_set_ids: List[int]) -> List[ProductSetsTag]:
        """
        Get the product tags of the products within given product sets ids.
        
        Args:
            product_set_ids: List of ProductSet ids (max 100)
            
        Returns:
            List of product set tags
        """
        params = {"productSetIds[]": product_set_ids}
        
        response_data = self._client._make_request_sync(
            "GET", 
            "/v2/product-sets/tags", 
            params=params
        )
        
        return [ProductSetsTag(**item) for item in response_data]
    
    async def get_product_sets_tags_async(self, product_set_ids: List[int]) -> List[ProductSetsTag]:
        """
        Get the product tags of the products within given product sets ids (async).
        
        Args:
            product_set_ids: List of ProductSet ids (max 100)
            
        Returns:
            List of product set tags
        """
        params = {"productSetIds[]": product_set_ids}
        
        response_data = await self._client._make_request_async(
            "GET", 
            "/v2/product-sets/tags", 
            params=params
        )
        
        return [ProductSetsTag(**item) for item in response_data]
    
    def get_product_set_prices(self, product_set_id: int) -> List[PriceRead]:
        """
        Get list of multi prices for all products within product set.
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            
        Returns:
            List of prices for all products in the product set
        """
        response_data = self._client._make_request_sync(
            "GET", 
            f"/v2/product-set/{product_set_id}/prices"
        )
        
        return [PriceRead(**item) for item in response_data]
    
    async def get_product_set_prices_async(self, product_set_id: int) -> List[PriceRead]:
        """
        Get list of multi prices for all products within product set (async).
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            
        Returns:
            List of prices for all products in the product set
        """
        response_data = await self._client._make_request_async(
            "GET", 
            f"/v2/product-set/{product_set_id}/prices"
        )
        
        return [PriceRead(**item) for item in response_data]
    
    def update_product_set_prices(self, product_set_id: int, payload: List[UpdateProductSetPriceRequest]) -> List[PriceRead]:
        """
        Update prices of a product set.
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            payload: List of price updates for products in the set
            
        Returns:
            List of updated prices
        """
        # Convert each item in the payload list to a dict and prepare it
        prepared_payload = [
            self._prepare_payload(item.model_dump(exclude_none=True))
            for item in payload
        ]
        
        response_data = self._client._make_request_sync(
            "PUT", 
            f"/v2/product-set/{product_set_id}/prices", 
            json_data=prepared_payload
        )
        
        # Handle both single object and list responses
        if isinstance(response_data, list):
            return [PriceRead(**item) for item in response_data]
        else:
            return [PriceRead(**response_data)]
    
    async def update_product_set_prices_async(self, product_set_id: int, payload: List[UpdateProductSetPriceRequest]) -> List[PriceRead]:
        """
        Update prices of a product set (async).
        
        Args:
            product_set_id: Numeric ID of the ProductSet
            payload: List of price updates for products in the set
            
        Returns:
            List of updated prices
        """
        # Convert each item in the payload list to a dict and prepare it
        prepared_payload = [
            self._prepare_payload(item.model_dump(exclude_none=True))
            for item in payload
        ]
        
        response_data = await self._client._make_request_async(
            "PUT", 
            f"/v2/product-set/{product_set_id}/prices", 
            json_data=prepared_payload
        )
        
        # Handle both single object and list responses
        if isinstance(response_data, list):
            return [PriceRead(**item) for item in response_data]
        else:
            return [PriceRead(**response_data)]
    
    def get_quality_control_status(self, params: GetQualityControlStatusRequest) -> List[QualityControlStatus]:
        """
        Get information about quality control status of the ProductSet.
        
        Args:
            params: Request parameters with product set IDs
            
        Returns:
            List of quality control statuses for requested product sets
        """
        response_data = self._client._make_request_sync(
            "GET", 
            "/v2/product-set/quality-control-status", 
            params=params.to_api_params()
        )
        
        return [QualityControlStatus(**item) for item in response_data]

    async def get_quality_control_status_async(self, params: GetQualityControlStatusRequest) -> List[QualityControlStatus]:
        """
        Get information about quality control status of the ProductSet (async).
        
        Args:
            params: Request parameters with product set IDs
            
        Returns:
            List of quality control statuses for requested product sets
        """
        response_data = await self._client._make_request_async(
            "GET", 
            "/v2/product-set/quality-control-status", 
            params=params.to_api_params()
        )
        
        return [QualityControlStatus(**item) for item in response_data]

    def get_images_by_sku(self, params: GetImagesBySKURequest) -> List[ProductImageBySKU]:
        """
        Get the URL of main images by product shop SKU or Seller SKU.
        
        Args:
            params: Request parameters with product SKUs
            
        Returns:
            List of product images with their SKUs
        """
        response_data = self._client._make_request_sync(
            "GET", 
            "/v2/product-set/images-by-sku", 
            params=params.to_api_params()
        )
        
        return [ProductImageBySKU(**item) for item in response_data]

    async def get_images_by_sku_async(self, params: GetImagesBySKURequest) -> List[ProductImageBySKU]:
        """
        Get the URL of main images by product shop SKU or Seller SKU (async).
        
        Args:
            params: Request parameters with product SKUs
            
        Returns:
            List of product images with their SKUs
        """
        response_data = await self._client._make_request_async(
            "GET", 
            "/v2/product-set/images-by-sku", 
            params=params.to_api_params()
        )
        
        return [ProductImageBySKU(**item) for item in response_data]
