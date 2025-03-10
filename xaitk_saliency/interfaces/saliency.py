import abc
from typing import Any, Iterable, Sequence, Tuple, Type, TypeVar

import numpy as np
import PIL.Image
from smqtk_core import Plugfigurable
from smqtk_descriptors import DescriptorElement, DescriptorGenerator


T = TypeVar("T", bound="SaliencyBlackbox")


class SaliencyBlackbox (Plugfigurable):
    """
    Blackbox function that produces some floating point scalar value for a
    given descriptor element.
    """

    @classmethod
    def from_iqr_session(
        cls: Type["SaliencyBlackbox"],
        iqrs: Any,  # "IqrSession"
        descr_generator: DescriptorGenerator,
        base_image: PIL.Image.Image
    ) -> "SaliencyBlackbox":
        """
        Create an ``SaliencyBlackbox`` instance from an
        :class:`smqtk.iqr.IqrSession` instance.

        Not all implementations of ``SaliencyBlackbox`` implement
        this method and may raise a ``NotImplementedError`` exception.

        :raises NotImplementedError:
            Construction from a ``IqrSession`` is not defined for this
            implementation.

        :param smqtk.iqr.IqrSession iqrs:
            An :py:class:`smqtk.iqr.IqrSession` instance to seed construction
            if a blackbox instance.
        :param descr_generator:
            Descriptor generator instance.
        :param base_image:
            A :py:class:`PIL.Image.Image` over which a saliency map may be
            generated.

        :return: A new instance of of a class implementing the
            ``SaliencyBlackbox`` class.
        """
        raise NotImplementedError("The ``from_iqr_session`` classmethod is "
                                  "not implemented for class ``{}``."
                                  .format(cls.__name__))

    @abc.abstractmethod
    def transform(self, descriptors: Iterable[DescriptorElement]) -> np.ndarray:
        """
        Transform some number of descriptor elements into a saliency scalar
        values.

        :param descriptors:
            Descriptors to get the saliency values of.

        :return: The floating-point saliency value for the given descriptor.
        """


class ImageSaliencyAugmenter (Plugfigurable):
    """
    Algorithm that yields a number of augmentations of an input image, as well
    as preserved-area masks, used for use in saliency map generation.
    """

    @abc.abstractmethod
    def augment(
        self,
        image_mat: np.ndarray
    ) -> Tuple[Sequence[PIL.Image.Image], np.ndarray]:
        """
        Takes in an image matrix and returns its augmented version

        :param image_mat:
            Image matrix to be augmented. This should be in the format
            [height, width [,channel]].

        :return: A sequence of augmented images as well as congruently sized
            array of masks that indicate the regions in the augmented images
            that are unmodified with respect to the input image (preserved
            regions).

            Returned augmented images should have the same height, width and
            channel format as the input image matrix.

            Returned masks should be in the dimension format
            [index, height, width] with the boolean data type.
        """


class ImageSaliencyMapGenerator (Plugfigurable):
    """
    Interface for the method of generation of a saliency map given an image
    augmentation and blackbox algorithms.
    """

    @abc.abstractmethod
    def generate(
        self,
        image_mat: np.ndarray,
        augmenter: ImageSaliencyAugmenter,
        descriptor_generator: DescriptorGenerator,
        blackbox: SaliencyBlackbox
    ) -> PIL.Image.Image:
        """
        Generate an image saliency heat-map matrix given a blackbox's behavior
        over the descriptions of an augmented base image.

        :param image_mat:
            Numpy image matrix of the format [height, width [,channel]] that is
            to be augmented.
        :param augmenter:
            Augmentation algorithm following
            the :py:class:`ImageSaliencyAugmenter` interface.
        :param descriptor_generator:
            A descriptor generation algorithm following
            the :py:class:`smqtk.algorithms.DescriptorGenerator` interface.
        :param blackbox:
            Blackbox algorithm implementation following
            the :py:class:`SaliencyBlackbox` interface.

        :return: A PIL Image with the same height and width properties as the
            input image.

            :py:class:`numpy.ndarray` matrix of the same [height, width]
            shape as the input image matrix but of floating-point type within
            the range of [0,1], where areas of higher value represent more
            salient regions according to the given blackbox algorithm.
        """
