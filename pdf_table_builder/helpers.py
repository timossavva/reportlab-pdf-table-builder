def calculate_image_dimensions_and_keep_aspect_ratio(img_width, img_height, img_desired_width=None,
                                                     img_desired_height=None):
    # Determine the dimensions of the image in the overview
    print_width = img_width
    print_height = img_height
    image_aspect = float(img_width) / float(img_height)
    # If the image width exceeds the desired width then calculate the width and height to fit the desired width.
    if img_desired_width is not None:
        if img_width > img_desired_width:
            print_width = img_desired_width
            print_height = print_width / image_aspect
    # If the image width exceeds the desired height then calculate the height and height to fit the desired width.
    if img_desired_height is not None:
        if print_height > img_desired_height:
            print_height = img_desired_height
            print_width = image_aspect * print_height

    return print_width, print_height
